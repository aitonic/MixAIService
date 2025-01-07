import os
import sys
import unittest

from src.app.model_components.text_segmentation.chinese_segmentation import (
    ChineseSegmentation,
)
from src.app.model_components.text_segmentation.segmentation_context import (
    SegmentationContext,
)


class TestTextSegmentation(unittest.TestCase):
    def test_chinese_segmentation(self) -> None:
        strategy = ChineseSegmentation()
        context = SegmentationContext(strategy)

        text1 = "你好。这是一个测试句子！这是另一个句子？"
        expected1 = ["你好。", "这是一个测试句子！", "这是另一个句子？"]
        self.assertEqual(context.segment_text(text1), expected1)

        text2 = "第一段。\n\n第二段，包含一个句子。"
        expected2 = ["第一段。", "第二段，包含一个句子。"]
        self.assertEqual(context.segment_text(text2), expected2)

        text3 = "没有句号的段落"
        expected3 = ["没有句号的段落"]
        self.assertEqual(context.segment_text(text3), expected3)

        text4 = "  有空格的句子。  "
        expected4 = ["有空格的句子。"]
        self.assertEqual(context.segment_text(text4), expected4)

        text5 = "  \n\n  多个空行。\n  "
        expected5 = ["多个空行。"]
        self.assertEqual(context.segment_text(text5), expected5)

        text6 = ""
        expected6 = []
        self.assertEqual(context.segment_text(text6), expected6)

        text7 = "你好。\n这是一个测试句子！\n这是另一个句子？"
        expected7 = ["你好。", "这是一个测试句子！", "这是另一个句子？"]
        self.assertEqual(context.segment_text(text7), expected7)

    def test_strategy_switching(self) -> None:
        strategy1 = ChineseSegmentation()
        context = SegmentationContext(strategy1)
        text = "你好。这是一个测试句子！"
        expected1 = ["你好。", "这是一个测试句子！"]
        self.assertEqual(context.segment_text(text), expected1)

        # You can add another strategy here and test switching
        # For example:
        # class DummyStrategy(SegmentationStrategy):
        #     def segment(self, text: str) -> list[str]:
        #         return [text]
        # strategy2 = DummyStrategy()
        # context.set_strategy(strategy2)
        # expected2 = ["你好。这是一个测试句子！"]
        # self.assertEqual(context.segment_text(text), expected2)


if __name__ == "__main__":
    unittest.main()
