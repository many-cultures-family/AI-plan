"""마스킹 프로토타입 테스트. 모든 값은 가짜 데이터다.

실행: prototypes/masking/ 에서 `python3 -m unittest -v`
"""

import unittest

from masking import OcrLine, detect_pii, mask_ocr_lines

# 가짜 값 (실제 사람 정보 아님)
FAKE_RRN = "900101-1234567"
FAKE_ARN = "900101-5234567"
FAKE_PHONE = "010-0000-1234"
FAKE_EMAIL = "test.user@example.com"
FAKE_ADDR = "서울특별시 가나구 다라로 12"
FAKE_NAME = "홍길동"


def mask(*texts: str):
    return mask_ocr_lines([OcrLine(text=t) for t in texts])


class TestMaskOcrLines(unittest.TestCase):
    """US-01 정상: 문서 속 개인정보를 모두 가린다 / R1: 가린 텍스트만 LLM에 보낸다."""

    def test_us01_value_patterns_masked(self):
        r = mask(
            f"주민등록번호 {FAKE_RRN}",
            f"외국인등록번호 {FAKE_ARN}",
            f"휴대전화 {FAKE_PHONE}",
            f"이메일 {FAKE_EMAIL}",
        )
        for raw in (FAKE_RRN, FAKE_ARN, FAKE_PHONE, FAKE_EMAIL):
            self.assertNotIn(raw, r.masked_text)
        self.assertIn("[주민등록번호]", r.masked_text)
        self.assertIn("[외국인등록번호]", r.masked_text)
        self.assertIn("[전화번호]", r.masked_text)
        self.assertIn("[이메일]", r.masked_text)
        self.assertFalse(r.residual)

    def test_us01_label_values_masked(self):
        r = mask(f"성명: {FAKE_NAME}", "생년월일 1990.01.01", f"주소: {FAKE_ADDR}")
        self.assertNotIn(FAKE_NAME, r.masked_text)
        self.assertNotIn("1990.01.01", r.masked_text)
        self.assertNotIn("다라로", r.masked_text)
        self.assertEqual(r.lines[0].text, "성명: [이름]")

    def test_us01_two_labels_in_one_line(self):
        r = mask(f"성명 {FAKE_NAME} 생년월일 1990.01.01")
        self.assertEqual(r.lines[0].text, "성명 [이름] 생년월일 [생년월일]")

    def test_us01_name_followed_by_phone(self):
        r = mask(f"성명: {FAKE_NAME} {FAKE_PHONE}")
        self.assertEqual(r.lines[0].text, "성명: [이름] [전화번호]")

    def test_us01_foreign_name_label(self):
        r = mask("Name: NGUYEN VAN A")
        self.assertNotIn("NGUYEN", r.masked_text)

    def test_l1_blank_form_field_kept(self):
        """빈칸 라벨은 그대로 둔다. L1이 칸을 추론하려면 라벨이 필요하다."""
        r = mask("성명: ________", "주소 (          )", "전화번호")
        self.assertEqual(r.masked_text, "성명: ________\n주소 (          )\n전화번호")
        self.assertEqual(r.findings, [])

    def test_l1_non_personal_text_kept(self):
        r = mask("신청일 2026.11.17", "※ 해당 칸에 체크하세요", "제1조(목적)")
        self.assertEqual(r.masked_text, "신청일 2026.11.17\n※ 해당 칸에 체크하세요\n제1조(목적)")

    def test_l1_hyphen_dates_kept(self):
        """신청일·기한 날짜는 개인정보가 아니고 L1에 필요하다."""
        r = mask("신청일 2026-11-17", "기한 2026/12/31")
        self.assertEqual(r.masked_text, "신청일 2026-11-17\n기한 2026/12/31")

    def test_us01_birth_date_with_hyphen_masked(self):
        r = mask("생년월일: 1990-01-01")
        self.assertEqual(r.lines[0].text, "생년월일: [생년월일]")

    def test_us01_label_with_parenthesis(self):
        r = mask(f"성명(한글) {FAKE_NAME}")
        self.assertEqual(r.lines[0].text, "성명(한글) [이름]")

    def test_us01_international_phone(self):
        r = mask("Tel: +82-10-0000-1234")
        self.assertEqual(r.lines[0].text, "Tel: [전화번호]")

    @unittest.expectedFailure
    def test_known_limit_name_in_sentence(self):
        """[한계] 라벨 없이 문장 속에 있는 이름은 규칙으로 못 찾는다. data-flow.md 4절 참고."""
        r = mask(f"저는 {FAKE_NAME}입니다")
        self.assertNotIn(FAKE_NAME, r.masked_text)

    def test_unlabeled_long_number_masked(self):
        """계좌·여권 번호처럼 종류를 모르는 긴 숫자도 가린다 (넘치게 가리는 쪽을 택함)."""
        r = mask("입금 계좌 110-123-456789")
        self.assertNotIn("456789", r.masked_text)

    def test_bbox_and_page_kept(self):
        bbox = {"page": 2, "x": 0.1, "y": 0.2, "w": 0.3, "h": 0.04}
        r = mask_ocr_lines([OcrLine(text=f"전화 {FAKE_PHONE}", page=2, bbox=bbox)])
        self.assertEqual(r.lines[0].page, 2)
        self.assertEqual(r.lines[0].bbox, bbox)

    def test_r8_findings_hold_no_raw_value(self):
        """R8: 감지 결과에는 위치·종류만 있고 원문 값은 없다."""
        r = mask(f"전화 {FAKE_PHONE}")
        self.assertEqual(len(r.findings), 1)
        self.assertNotIn(FAKE_PHONE, repr(r.findings))
        self.assertEqual(r.findings[0].kind, "phone")
        self.assertEqual(r.findings[0].line, 0)


class TestDetectPii(unittest.TestCase):
    """F-07·R7: 서술형 답변은 가리지 않고 위치만 알려 준다."""

    def test_r7_spans_point_to_value(self):
        text = f"연락은 {FAKE_PHONE} 이나 {FAKE_EMAIL} 로 주세요"
        spans = detect_pii(text)
        self.assertEqual([s.kind for s in spans], ["phone", "email"])
        self.assertEqual(text[spans[0].start : spans[0].end], FAKE_PHONE)
        self.assertEqual(text[spans[1].start : spans[1].end], FAKE_EMAIL)

    def test_r7_plain_answer_has_no_spans(self):
        self.assertEqual(detect_pii("한국어를 더 배우고 싶어서 신청합니다."), [])


if __name__ == "__main__":
    unittest.main()
