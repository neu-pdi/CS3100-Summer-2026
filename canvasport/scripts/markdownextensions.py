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
