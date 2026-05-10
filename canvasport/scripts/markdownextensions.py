import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension


class MarginNotesBlockProcessor(BlockProcessor):
    RE_MARGIN_NOTES_START = r'^ *\+{3,}\s*Margin note\s*\+{3,}\n'
    RE_MARGIN_NOTES_END = r'\n *\+{3,}\s*$'

    def test(self, parent, block):
        return re.match(self.RE_MARGIN_NOTES_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_MARGIN_NOTES_START, '', blocks[0])

        for block_num, block in enumerate(blocks):
            if re.search(self.RE_MARGIN_NOTES_END, block):
                blocks[block_num] = re.sub(self.RE_MARGIN_NOTES_END, '', block)
                element = etree.SubElement(parent, 'blockquote')
                element.set(
                    'style',
                    'display: inline-block; border: 1px solid #ccb; border-left: 0.4rem solid #ccb; background: hsl(60, 29%, 94%);',
                )
                self.parser.parseBlocks(element, blocks[0:block_num + 1])
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        blocks[0] = original_block
        return False


class MarginNotesExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(MarginNotesBlockProcessor(md.parser), 'marginnotes', 175)


class TodoBlockProcessor(BlockProcessor):
    RE_TODO_START = r'^ *\+{3,}\s*Todo\s*\+{3,}\n*'
    RE_TODO_END = r' *\+{3,}\s*$'

    def test(self, parent, block):
        return re.match(self.RE_TODO_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_TODO_START, '', blocks[0])

        for block_num, block in enumerate(blocks):
            if re.search(self.RE_TODO_END, block):
                blocks[block_num] = re.sub(self.RE_TODO_END, '', block)
                element = etree.SubElement(parent, 'div')
                element.set('style', 'display:block; line-height: 1.4;')
                element = etree.SubElement(element, 'blockquote')
                element.set(
                    'style',
                    'padding: 0px 0px 0.5em 10px; border-left-style: solid; border-width: 5px; border-color: orange; background-color: #ffebcd;',
                )
                element = etree.SubElement(element, 'div')
                element.set(
                    'style',
                    'font-weight: bold; font-style: italic; background-color: #ffb167; padding: 5px 0px 0px 5px; margin-left: -10px;',
                )
                element.text = 'To do:'
                element = etree.SubElement(element, 'div')
                element.set(
                    'style',
                    'font-weight:normal; font-style:normal;display: block; margin: 0 0 1em 0; line-height: 1.4;background-color: #ffebcd; padding: 0px 0px 0px 5px;margin-left: -5px; margin-top:-5px',
                )
                self.parser.parseBlocks(element, blocks[0:block_num + 1])
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        blocks[0] = original_block
        return False


class TodoExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(TodoBlockProcessor(md.parser), 'todo', 175)


class IncerciseBlockProcessor(BlockProcessor):
    RE_INCERCISE_START = r'^ *\+{3,}\s*Incercise\s*\+{3,}\n'
    RE_INCERCISE_END = r'\n *\+{3,}\s*$'

    def test(self, parent, block):
        return re.match(self.RE_INCERCISE_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_INCERCISE_START, '', blocks[0])

        for block_num, block in enumerate(blocks):
            if re.search(self.RE_INCERCISE_END, block):
                blocks[block_num] = re.sub(self.RE_INCERCISE_END, '', block)
                element = etree.SubElement(parent, 'div')
                element.set('style', 'display:block; line-height: 1.4;')
                element = etree.SubElement(element, 'blockquote')
                element.set(
                    'style',
                    'padding: 0px 0px 0.5em 10px; border-left-style: solid; border-width: 5px; border-color: red; background-color: #ffebcd;',
                )
                element = etree.SubElement(element, 'div')
                element.set(
                    'style',
                    'font-weight: bold; font-style: italic; background-color: #FD7B67; padding: 5px 0px 0px 5px; margin-left: -10px;',
                )
                element.text = 'Do Now!'
                element = etree.SubElement(element, 'div')
                element.set(
                    'style',
                    'font-weight:bold; font-style:normal;display: block; margin: 0 0 1em 0; line-height: 1.4;background-color: #ffebcd; padding: 0px 0px 0px 5px;margin-left: -5px; margin-top:-5px',
                )
                self.parser.parseBlocks(element, blocks[0:block_num + 1])
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        blocks[0] = original_block
        return False


class IncerciseExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(IncerciseBlockProcessor(md.parser), 'incercise', 175)


class ExerciseBlockProcessor(BlockProcessor):
    RE_EXERCISE_START = r'^ *\+{3,}\s*Exercise\s*\+{3,}\n'
    RE_EXERCISE_END = r'\n *\+{3,}\s*$'

    def test(self, parent, block):
        return re.match(self.RE_EXERCISE_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_EXERCISE_START, '', blocks[0])

        for block_num, block in enumerate(blocks):
            if re.search(self.RE_EXERCISE_END, block):
                blocks[block_num] = re.sub(self.RE_EXERCISE_END, '', block)
                element = etree.SubElement(parent, 'div')
                element.set('style', 'display:block; line-height: 1.4;')
                element = etree.SubElement(element, 'blockquote')
                element.set(
                    'style',
                    'padding: 0px 0px 0.5em 10px; border-left-style: solid; border-width: 5px; border-color: orange; background-color: #ffebcd;',
                )
                element = etree.SubElement(element, 'div')
                element.set(
                    'style',
                    'font-weight: bold; font-style: italic; background-color: #ffb167; padding: 5px 0px 0px 5px; margin-left: -10px;',
                )
                element.text = 'Do Now!'
                element = etree.SubElement(element, 'div')
                element.set(
                    'style',
                    'font-weight:normal; font-style:normal;display: block; margin: 0 0 1em 0; line-height: 1.4;background-color: #ffebcd; padding: 0px 0px 0px 5px;margin-left: -5px; margin-top:-5px',
                )
                self.parser.parseBlocks(element, blocks[0:block_num + 1])
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        blocks[0] = original_block
        return False


class ExerciseExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(ExerciseBlockProcessor(md.parser), 'exercise', 175)


class AdmonitionFenceBlockProcessor(BlockProcessor):
    RE_END = r'(^|\n) *:{3,}\s*$'

    def __init__(
        self,
        parser,
        kind: str,
        outer_style: str,
        heading_text: str,
        heading_style: str,
        body_style: str,
    ):
        super().__init__(parser)
        self.kind = kind
        self.outer_style = outer_style
        self.heading_text = heading_text
        self.heading_style = heading_style
        self.body_style = body_style
        self.re_start = re.compile(
            rf'^ *:{{3,}}[ \t]*{re.escape(kind)}(?:[ \t]+.*)?[ \t]*(?:\n|$)',
            flags=re.IGNORECASE,
        )

    def test(self, parent, block):
        return self.re_start.match(block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = self.re_start.sub('', blocks[0])

        for block_num, block in enumerate(blocks):
            if re.search(self.RE_END, block):
                blocks[block_num] = re.sub(self.RE_END, '', block)
                container = etree.SubElement(parent, 'div')
                container.set('style', 'display:block; line-height: 1.4;')
                element = etree.SubElement(container, 'blockquote')
                element.set('style', self.outer_style)
                heading = etree.SubElement(element, 'div')
                heading.set('style', self.heading_style)
                heading.text = self.heading_text
                body = etree.SubElement(element, 'div')
                body.set('style', self.body_style)
                self.parser.parseBlocks(body, blocks[0:block_num + 1])
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        blocks[0] = original_block
        return False


class NoteExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            AdmonitionFenceBlockProcessor(
                md.parser,
                kind='note',
                outer_style='display: inline-block; border: 1px solid #ccb; border-left: 0.4rem solid #ccb; background: hsl(60, 29%, 94%);',
                heading_text='Note',
                heading_style='font-weight: bold; font-style: italic; background: #e7e7c9; border-bottom: 1px solid #ccb; padding: 4px 8px;',
                body_style='display:block; margin: 0; padding: 0.6em 0.8em; line-height: 1.4;',
            ),
            'note-fence',
            175,
        )


class TipExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            AdmonitionFenceBlockProcessor(
                md.parser,
                kind='tip',
                outer_style='display: inline-block; border: 1px solid #ccb; border-left: 0.4rem solid #ccb; background: hsl(60, 29%, 94%);',
                heading_text='Tip',
                heading_style='font-weight: bold; font-style: italic; background: #e7e7c9; border-bottom: 1px solid #ccb; padding: 4px 8px;',
                body_style='display:block; margin: 0; padding: 0.6em 0.8em; line-height: 1.4;',
            ),
            'tip-fence',
            175,
        )


class InfoExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            AdmonitionFenceBlockProcessor(
                md.parser,
                kind='info',
                outer_style='display: inline-block; border: 1px solid #ccb; border-left: 0.4rem solid #ccb; background: hsl(60, 29%, 94%);',
                heading_text='Info',
                heading_style='font-weight: bold; font-style: italic; background: #e7e7c9; border-bottom: 1px solid #ccb; padding: 4px 8px;',
                body_style='display:block; margin: 0; padding: 0.6em 0.8em; line-height: 1.4;',
            ),
            'info-fence',
            175,
        )


class WarningExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            AdmonitionFenceBlockProcessor(
                md.parser,
                kind='warning',
                outer_style='padding: 0px 0px 0.5em 10px; border-left-style: solid; border-width: 5px; border-color: red; background-color: #ffebcd;',
                heading_text='Warning',
                heading_style='font-weight: bold; font-style: italic; background-color: #FD7B67; padding: 5px 0px 0px 5px; margin-left: -10px;',
                body_style='font-weight:bold; font-style:normal;display: block; margin: 0 0 1em 0; line-height: 1.4;background-color: #ffebcd; padding: 0px 0px 0px 5px;margin-left: -5px; margin-top:-5px',
            ),
            'warning-fence',
            175,
        )


class CautionExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            AdmonitionFenceBlockProcessor(
                md.parser,
                kind='caution',
                outer_style='padding: 0px 0px 0.5em 10px; border-left-style: solid; border-width: 5px; border-color: red; background-color: #ffebcd;',
                heading_text='Caution',
                heading_style='font-weight: bold; font-style: italic; background-color: #FD7B67; padding: 5px 0px 0px 5px; margin-left: -10px;',
                body_style='font-weight:bold; font-style:normal;display: block; margin: 0 0 1em 0; line-height: 1.4;background-color: #ffebcd; padding: 0px 0px 0px 5px;margin-left: -5px; margin-top:-5px',
            ),
            'caution-fence',
            175,
        )


class DangerExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            AdmonitionFenceBlockProcessor(
                md.parser,
                kind='danger',
                outer_style='padding: 0px 0px 0.5em 10px; border-left-style: solid; border-width: 5px; border-color: orange; background-color: #ffebcd;',
                heading_text='Danger',
                heading_style='font-weight: bold; font-style: italic; background-color: #ffb167; padding: 5px 0px 0px 5px; margin-left: -10px;',
                body_style='font-weight:normal; font-style:normal;display: block; margin: 0 0 1em 0; line-height: 1.4;background-color: #ffebcd; padding: 0px 0px 0px 5px;margin-left: -5px; margin-top:-5px',
            ),
            'danger-fence',
            175,
        )


class AsciiArtBlockProcessor(BlockProcessor):
    RE_ASCII_ART_START = r'\+{3,}\s*Ascii art\s*\+{3,}'
    RE_ASCII_ART_END = r'\+{3,}\s*$'

    def test(self, parent, block):
        return re.match(self.RE_ASCII_ART_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_ASCII_ART_START, '', blocks[0])

        for block_num, block in enumerate(blocks):
            if re.search(self.RE_ASCII_ART_END, block):
                blocks[block_num] = re.sub(self.RE_ASCII_ART_END, '', block)
                element = etree.SubElement(parent, 'pre')
                element.set('style', 'font-family: Source Code Pro,monospace;font-size: 1rem;')
                self.parser.parseBlocks(element, blocks[0:block_num + 1])
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        blocks[0] = original_block
        return False


class AsciiArtExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(AsciiArtBlockProcessor(md.parser), 'ascii-art', 175)
