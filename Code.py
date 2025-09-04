"""
Created By Mahdi Dehghan (Mahdiqoo)
https://github.com/Mahdiqoo
Version 1.00
"""
import sys
import os
import re
import ast
import subprocess
import platform
import keyword
from typing import List, Dict, Optional, Tuple, Any, Set

from PyQt5.QtCore import (
    QObject, Qt, QThread, pyqtSignal, QTimer, QSettings, QRect,
    QProcess, QStringListModel, QSize, QPoint, QProcessEnvironment
)
from PyQt5.QtWidgets import (
QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
QSplitter, QTreeWidget, QTreeWidgetItem, QComboBox,
QToolBar, QAction, QFileDialog, QMessageBox, QTabWidget,
QLabel, QPushButton, QLineEdit, QDialog, QDialogButtonBox,
QCheckBox, QGroupBox, QGridLayout, QPlainTextEdit,
QStatusBar, QProgressBar, QMenu, QListWidget,
QCompleter, QTextBrowser, QColorDialog, QFontDialog,
QInputDialog, QTextEdit
)
from PyQt5.QtGui import (
    QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor,
    QKeySequence, QPainter, QTextDocument, QTextOption,
    QBrush, QKeyEvent, QMouseEvent, QTextFormat
)

# =============================
# Syntax Highlighter
# =============================

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Advanced Python syntax highlighter with multiple themes"""

    def __init__(self, parent=None, theme="dark"):
        super().__init__(parent)
        self.theme = theme
        self.highlighting_rules: List[Tuple[re.Pattern, QTextCharFormat]] = []
        self.setup_highlighting_rules()

    def _make_format(self, color: QColor, bold=False, italic=False) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setForeground(QBrush(color))
        if bold:
            f.setFontWeight(QFont.Bold)
        if italic:
            f.setFontItalic(True)
        return f

    def setup_highlighting_rules(self):
        """Setup highlighting rules based on theme"""
        self.highlighting_rules = []

        if self.theme == "dark":
            colors = {
                'keyword': QColor(86, 156, 214),
                'builtin': QColor(220, 220, 170),
                'string': QColor(206, 145, 120),
                'number': QColor(181, 206, 168),
                'comment': QColor(106, 153, 85),
                'function': QColor(220, 220, 170),
                'class': QColor(78, 201, 176),
                'operator': QColor(212, 212, 212),
                'decorator': QColor(255, 198, 109),
                'self': QColor(148, 161, 255),
            }
        else:
            colors = {
                'keyword': QColor(0, 0, 255),
                'builtin': QColor(128, 0, 128),
                'string': QColor(163, 21, 21),
                'number': QColor(9, 134, 88),
                'comment': QColor(0, 128, 0),
                'function': QColor(128, 0, 128),
                'class': QColor(0, 128, 128),
                'operator': QColor(0, 0, 0),
                'decorator': QColor(128, 128, 0),
                'self': QColor(0, 0, 255),
            }

        # Keywords
        keyword_format = self._make_format(colors['keyword'], bold=True)
        python_keywords = sorted(set(keyword.kwlist + ['True', 'False', 'None']))
        for word in python_keywords:
            pattern = re.compile(r'\b' + re.escape(word) + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))

        # Builtins
        builtin_format = self._make_format(colors['builtin'])
        builtins_list = [
            'abs', 'all', 'any', 'bin', 'bool', 'bytearray', 'bytes', 'callable',
            'chr', 'classmethod', 'compile', 'complex', 'delattr', 'dict', 'dir',
            'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
            'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex',
            'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len',
            'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object',
            'oct', 'open', 'ord', 'pow', 'print', 'property', 'range', 'repr',
            'reversed', 'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod',
            'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip', '__import__'
        ]
        for b in builtins_list:
            self.highlighting_rules.append((re.compile(r'\b' + re.escape(b) + r'\b'), builtin_format))

        # self
        self_format = self._make_format(colors['self'], bold=True)
        self.highlighting_rules.append((re.compile(r'\bself\b'), self_format))

        # Strings (single-line)
        string_format = self._make_format(colors['string'])
        self.highlighting_rules.append((re.compile(r'"([^"\\\n]|\\.)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'([^'\\\n]|\\.)*'"), string_format))
        self.highlighting_rules.append((re.compile(r'r"([^"\\\n]|\\.)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"r'([^'\\\n]|\\.)*'"), string_format))
        self.highlighting_rules.append((re.compile(r'R"([^"\\\n]|\\.)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"R'([^'\\\n]|\\.)*'"), string_format))
        self.highlighting_rules.append((re.compile(r'f"([^"\\\n]|\\.)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"f'([^'\\\n]|\\.)*'"), string_format))
        self.highlighting_rules.append((re.compile(r'F"([^"\\\n]|\\.)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"F'([^'\\\n]|\\.)*'"), string_format))

        # Numbers
        number_format = self._make_format(colors['number'])
        self.highlighting_rules.append((re.compile(r'\b\d+\.?\d*([eE][+-]?\d+)?\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[xX][0-9a-fA-F]+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[bB][01]+\b'), number_format))
        self.highlighting_rules.append((re.compile(r'\b0[oO][0-7]+\b'), number_format))

        # Comments
        comment_format = self._make_format(colors['comment'], italic=True)
        self.highlighting_rules.append((re.compile(r'#.*$'), comment_format))

        # defs/classes/decorators/operators
        function_format = self._make_format(colors['function'], bold=True)
        self.highlighting_rules.append((re.compile(r'\bdef\s+(\w+)'), function_format))
        class_format = self._make_format(colors['class'], bold=True)
        self.highlighting_rules.append((re.compile(r'\bclass\s+(\w+)'), class_format))
        decorator_format = self._make_format(colors['decorator'])
        self.highlighting_rules.append((re.compile(r'@\w+'), decorator_format))
        operator_format = self._make_format(colors['operator'])
        for op in [r'\+\+', r'--', r'\+', r'-', r'\*', r'/', r'//', r'%', r'\*\*',
                   r'==', r'!=', r'<=', r'>=', r'<', r'>', r'=', r'<<', r'>>',
                   r'&', r'\|', r'\^', r'~']:
            self.highlighting_rules.append((re.compile(op), operator_format))

        # For multi-line strings
        self.triple_double = re.compile(r'"""')
        self.triple_single = re.compile(r"'''")
        self._ml_string_format = self._make_format(QColor(206, 145, 120))

    def highlightBlock(self, text: str):
        for pattern, fmt in self.highlighting_rules:
            try:
                for match in pattern.finditer(text):
                    start, end = match.span()
                    self.setFormat(start, end - start, fmt)
            except re.error:
                pass

        # Multiline triple-quoted strings
        self.setCurrentBlockState(0)
        in_multiline = self.previousBlockState() == 1
        for triple in (self.triple_double, self.triple_single):
            start = 0
            if not in_multiline:
                m = triple.search(text, start)
                start = m.start() if m else -1
            else:
                start = 0

            while start >= 0:
                m_end = triple.search(text, start + 3)
                if m_end:
                    end_index = m_end.end()
                    length = end_index - start
                    self.setCurrentBlockState(0)
                else:
                    self.setCurrentBlockState(1)
                    length = len(text) - start
                self.setFormat(start, length, self._ml_string_format)

                if m_end:
                    m2 = triple.search(text, end_index)
                    start = m2.start() if m2 else -1
                else:
                    start = -1

# =============================
# Code Editor & Gutter
# =============================

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
        self.setMouseTracking(True)

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            y = event.pos().y()
            editor = self.code_editor
            block = editor.firstVisibleBlock()
            blockNumber = block.blockNumber()
            top = editor.blockBoundingGeometry(block).translated(editor.contentOffset()).top()
            bottom = top + editor.blockBoundingRect(block).height()
            while block.isValid() and top <= event.pos().y():
                if block.isVisible() and bottom >= y:
                    line = blockNumber + 1
                    editor.toggle_breakpoint(line)
                    break
                block = block.next()
                blockNumber += 1
                top = bottom
                bottom = top + editor.blockBoundingRect(block).height()
        super().mousePressEvent(event)

class CodeEditor(QPlainTextEdit):
    """Enhanced code editor with numbers, breakpoints, completion, and click highlight"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize these FIRST
        self._structure_selections: List[QTextEdit.ExtraSelection] = []
        self._structure_color = QColor(120, 180, 255, 80)

        self._extra_selections_external: List[QTextEdit.ExtraSelection] = []
        self._execution_line: Optional[int] = None
        self.breakpoints: Set[int] = set()
        self._click_selection: Optional[QTextEdit.ExtraSelection] = None
        self._click_color = QColor(38, 79, 120, 140)  # default, overwritten by theme
        self.setup_editor()
        self.setup_auto_completion()
        self.setup_bracket_matching()

        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()
        self.zoom_level = 0

    def setup_editor(self):
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setWordWrapMode(QTextOption.NoWrap)

        # Tab width ~ 4 spaces
        metrics = self.fontMetrics()
        space_w = metrics.horizontalAdvance(' ')
        if hasattr(self, "setTabStopDistance"):
            self.setTabStopDistance(space_w * 4)
        elif hasattr(self, "setTabStopWidth"):
            self.setTabStopWidth(space_w * 4)

        self.highlighter = PythonSyntaxHighlighter(self.document())
        self.setAcceptDrops(True)

    # Group paste operations into a single undo step
    def insertFromMimeData(self, source):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        try:
            super().insertFromMimeData(source)
        finally:
            cursor.endEditBlock()

    def paste(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        try:
            super().paste()
        finally:
            cursor.endEditBlock()

    def replace_block_in_range(self, start_line: int, end_line: int, new_code: str) -> bool:
        """Replace entire block from start_line to end_line with new_code"""
        try:
            cursor = self.textCursor()
            start_block = self.document().findBlockByNumber(start_line - 1)
            if not start_block.isValid():
                return False
            start_pos = start_block.position()
            end_block = self.document().findBlockByNumber(end_line - 1)
            if not end_block.isValid():
                return False
            end_pos = end_block.position() + len(end_block.text())
            cursor.beginEditBlock()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            cursor.insertText(new_code)
            cursor.endEditBlock()
            return True
        except Exception as e:
            print(f"Error replacing block: {e}")
            return False

    def get_block_text(self, start_line: int, end_line: int) -> str:
        try:
            lines = self.toPlainText().splitlines()
            sidx = max(1, start_line) - 1
            eidx = min(len(lines), max(start_line, end_line))
            return '\n'.join(lines[sidx:eidx])
        except Exception:
            return ""

    def set_structure_highlight_color(self, qcolor: QColor):
        self._structure_color = qcolor
        if self._structure_selections:
            for sel in self._structure_selections:
                sel.format.setBackground(self._structure_color)
        self.highlight_current_line()

    def clear_structure_highlight(self):
        self._structure_selections = []
        self.highlight_current_line()

    def set_structure_highlight_range(self, start_line: int, end_line: int):
        self._structure_selections = []
        doc_blocks = self.blockCount()
        start = max(1, min(start_line, doc_blocks))
        end = max(start, min(end_line, doc_blocks))
        for ln in range(start, end + 1):
            block = self.document().findBlockByNumber(ln - 1)
            if block.isValid():
                cur = QTextCursor(block)
                sel = QTextEdit.ExtraSelection()
                sel.format.setBackground(self._structure_color)
                sel.format.setProperty(QTextFormat.FullWidthSelection, True)
                sel.cursor = cur
                self._structure_selections.append(sel)
        self.highlight_current_line()

    def compute_block_range(self, start_line: int) -> Tuple[int, int]:
        lines = self.toPlainText().splitlines()
        n = len(lines)
        idx = max(1, start_line) - 1
        if idx < 0 or idx >= n:
            return (start_line, start_line)

        def indent_of(s: str) -> int:
            s2 = s.replace('\t', '    ')
            return len(s2) - len(s2.lstrip(' '))

        header_indent = indent_of(lines[idx])
        end_idx = idx
        in_triple = None
        j = idx + 1
        while j < n:
            line = lines[j]
            if in_triple:
                if in_triple in line and (line.count(in_triple) % 2 == 1):
                    in_triple = None
                end_idx = j
                j += 1
                continue
            if '"""' in line or "'''" in line:
                for triple in ('"""', "'''"):
                    if line.count(triple) % 2 == 1:
                        in_triple = triple
                        break
            stripped = line.strip()
            if stripped == '':
                end_idx = j
                j += 1
                continue
            cur_indent = indent_of(line)
            if cur_indent <= header_indent and not line.lstrip().startswith(('@',)):
                break
            end_idx = j
            j += 1
        return (idx + 1, end_idx + 1)

    def rename_in_range(self, start_line: int, end_line: int, old_name: str, new_name: str) -> int:
        if old_name == new_name or not old_name:
            return 0
        lines = self.toPlainText().splitlines(True)
        sidx = max(1, start_line) - 1
        eidx = min(len(lines), max(start_line, end_line))
        segment = ''.join(lines[sidx:eidx])
        try:
            pattern = re.compile(r'\b' + re.escape(old_name) + r'\b')
        except re.error:
            return 0
        new_segment, count = pattern.subn(new_name, segment)
        if count > 0:
            cursor = self.textCursor()
            block_start = self.document().findBlockByNumber(sidx).position()
            if eidx - 1 >= 0:
                last_block = self.document().findBlockByNumber(eidx - 1)
                block_end = last_block.position() + len(last_block.text())
            else:
                block_end = block_start
            cursor.beginEditBlock()
            cursor.setPosition(block_start)
            cursor.setPosition(block_end, QTextCursor.KeepAnchor)
            cursor.insertText(new_segment)
            cursor.endEditBlock()
        return count

    def setup_auto_completion(self):
        self.completer_words = set()
        self.completer_words.update(keyword.kwlist)
        self.completer_words.update([
            'abs', 'all', 'any', 'bin', 'bool', 'bytearray', 'bytes', 'callable',
            'chr', 'classmethod', 'compile', 'complex', 'delattr', 'dict', 'dir',
            'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
            'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex',
            'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len',
            'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object',
            'oct', 'open', 'ord', 'pow', 'print', 'property', 'range', 'repr',
            'reversed', 'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod',
            'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip', '__import__'
        ])

        self.completer = QCompleter(sorted(list(self.completer_words)))
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)

    def setup_bracket_matching(self):
        self.brackets = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}

    # Theme-aware click highlight color
    def set_click_highlight_color(self, qcolor: QColor):
        self._click_color = qcolor
        self.highlight_current_line()

    # Breakpoints
    def toggle_breakpoint(self, line: int):
        if line in self.breakpoints:
            self.breakpoints.remove(line)
        else:
            self.breakpoints.add(line)
        self.line_number_area.update()

    def get_breakpoints(self) -> List[int]:
        return sorted(self.breakpoints)

    # Completion
    def insert_completion(self, completion):
        cursor = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        cursor.movePosition(QTextCursor.Left)
        cursor.movePosition(QTextCursor.EndOfWord)
        cursor.insertText(completion[-extra:])
        self.setTextCursor(cursor)

    def text_under_cursor(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText()

    # Events
    def keyPressEvent(self, event: QKeyEvent):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()
                return

        if event.key() == Qt.Key_Tab:
            self.handle_tab()
            return
        elif event.key() == Qt.Key_Backtab:
            self.handle_backtab()
            return
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.handle_return()
            return
        elif event.text() in self.brackets:
            self.handle_bracket_insertion(event.text())
            return
        elif event.key() == Qt.Key_Backspace:
            self.handle_backspace()
            return

        if event.modifiers() == Qt.ControlModifier:
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
                self.zoom_in()
                return
            elif event.key() == Qt.Key_Minus:
                self.zoom_out()
                return
            elif event.key() == Qt.Key_0:
                self.reset_zoom()
                return

        super().keyPressEvent(event)

        completion_prefix = self.text_under_cursor()
        if len(completion_prefix) > 2:
            self.update_completer_words()
            self.completer.setCompletionPrefix(completion_prefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
            cr = self.cursorRect()
            cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                        + self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        self.update_click_highlight()

    def update_click_highlight(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText()
        self._click_selection = None
        if word and re.match(r'\w+', word):
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(self._click_color)
            sel.cursor = cursor
            self._click_selection = sel
        self.highlight_current_line()

    # Editing helpers
    def handle_tab(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            self.indent_lines()
        else:
            cursor.insertText("    ")

    def handle_backtab(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            self.unindent_lines()
        else:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            line_text = cursor.selectedText()
            spaces_to_remove = min(4, len(line_text) - len(line_text.lstrip(' ')))
            if spaces_to_remove > 0:
                cursor = self.textCursor()
                for _ in range(spaces_to_remove):
                    cursor.deletePreviousChar()

    def handle_return(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        line_text = cursor.selectedText()
        indent = len(line_text) - len(line_text.lstrip(' '))
        if line_text.strip().endswith(':'):
            indent += 4
        cursor = self.textCursor()
        cursor.insertText('\n' + ' ' * indent)

    def handle_bracket_insertion(self, bracket):
        cursor = self.textCursor()
        closing_bracket = self.brackets[bracket]
        cursor.insertText(bracket + closing_bracket)
        cursor.movePosition(QTextCursor.Left)
        self.setTextCursor(cursor)

    def handle_backspace(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
        char_before = cursor.selectedText()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        char_after = cursor.selectedText()
        if char_before in self.brackets and char_after == self.brackets[char_before]:
            cursor = self.textCursor()
            cursor.deletePreviousChar()
            cursor.deleteChar()
        else:
            cursor = self.textCursor()
            cursor.deletePreviousChar()

    # FIXED: Group indent operations into single undo step
    def indent_lines(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()  # Start grouping
        try:
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.StartOfLine)
            while cursor.position() <= end:
                cursor.insertText("    ")
                end += 4
                if not cursor.movePosition(QTextCursor.Down):
                    break
                cursor.movePosition(QTextCursor.StartOfLine)
        finally:
            cursor.endEditBlock()  # End grouping

    # FIXED: Group unindent operations into single undo step
    def unindent_lines(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()  # Start grouping
        try:
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.StartOfLine)
            while cursor.position() <= end:
                line_start = cursor.position()
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                line_text = cursor.selectedText()
                spaces_to_remove = min(4, len(line_text) - len(line_text.lstrip(' ')))
                if spaces_to_remove > 0:
                    cursor.setPosition(line_start)
                    for _ in range(spaces_to_remove):
                        cursor.deleteChar()
                    end -= spaces_to_remove
                cursor.setPosition(line_start)
                if not cursor.movePosition(QTextCursor.Down):
                    break
                cursor.movePosition(QTextCursor.StartOfLine)
        finally:
            cursor.endEditBlock()  # End grouping

    def update_completer_words(self):
        text = self.toPlainText()
        words = re.findall(r'\b\w{3,}\b', text)
        self.completer_words.update(words)
        word_list = sorted(list(self.completer_words))
        model = QStringListModel(word_list)
        self.completer.setModel(model)

    # Zoom
    def zoom_in(self):
        self.zoom_level += 1
        font = self.font()
        font.setPointSize(font.pointSize() + 1)
        self.setFont(font)
        self.update_line_number_area_width(0)

    def zoom_out(self):
        if self.zoom_level > -5:
            self.zoom_level -= 1
            font = self.font()
            font.setPointSize(max(8, font.pointSize() - 1))
            self.setFont(font)
            self.update_line_number_area_width(0)

    def reset_zoom(self):
        self.zoom_level = 0
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        self.update_line_number_area_width(0)

    # Gutter
    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 8 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                         self.line_number_area.width(),
                                         rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def highlight_current_line(self):
        selections: List[QTextEdit.ExtraSelection] = []

        # Current line
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(50, 100, 150, 60)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)

        # Execution line
        if self._execution_line is not None:
            try:
                block = self.document().findBlockByNumber(self._execution_line - 1)
                if block.isValid():
                    cursor = QTextCursor(block)
                    cursor.clearSelection()
                    ex_sel = QTextEdit.ExtraSelection()
                    ex_sel.format.setBackground(QColor(255, 215, 0, 120))
                    ex_sel.format.setProperty(QTextFormat.FullWidthSelection, True)
                    ex_sel.cursor = cursor
                    selections.append(ex_sel)
            except Exception:
                pass

        # Clicked word selection
        if self._click_selection is not None:
            selections.append(self._click_selection)

        # External highlights (find/replace)
        selections.extend(self._extra_selections_external)

        if self._structure_selections:
            selections.extend(self._structure_selections)

        self.setExtraSelections(selections)

    def set_execution_line(self, line: Optional[int]):
        self._execution_line = line
        self.highlight_current_line()

    def set_external_highlights(self, extra: List[QTextEdit.ExtraSelection]):
        self._extra_selections_external = extra
        self.highlight_current_line()

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(240, 240, 240))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        height = self.fontMetrics().height()

        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QColor(120, 120, 120))
                painter.drawText(0, int(top), self.line_number_area.width() - 6,
                                 height, Qt.AlignRight, number)
                line = blockNumber + 1
                if line in self.breakpoints:
                    radius = 5
                    cx = 6
                    cy = int(top + (height / 2))
                    painter.setBrush(QBrush(QColor(200, 60, 60)))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(QPoint(cx + radius, cy), radius, radius)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

# =============================
# Code Structure Parser & Tree
# =============================

class CodeStructureParser:
    @staticmethod
    def parse_code(code_text: str) -> Dict:
        try:
            tree = ast.parse(code_text)
            structure = {
                'classes': [], 'functions': [], 'imports': [],
                'variables': [], 'decorators': [], 'constants': []
            }

            class CodeVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.current_class = None

                def visit_ClassDef(self, node):
                    methods, class_vars = [], []
                    def _unparse(x):
                        if hasattr(ast, 'unparse'):
                            try:
                                return ast.unparse(x)
                            except Exception:
                                return str(x)
                        return str(x)
                    decorators = [_unparse(dec) for dec in node.decorator_list]
                    old_class = self.current_class
                    self.current_class = node.name
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_decorators = [_unparse(dec) for dec in item.decorator_list]
                            methods.append({
                                'name': item.name, 'line': item.lineno,
                                'args': [arg.arg for arg in item.args.args],
                                'decorators': method_decorators,
                                'docstring': ast.get_docstring(item)
                            })
                        elif isinstance(item, ast.Assign):
                            for t in item.targets:
                                if isinstance(t, ast.Name):
                                    class_vars.append({'name': t.id, 'line': item.lineno})
                    structure['classes'].append({
                        'name': node.name, 'line': node.lineno,
                        'methods': methods, 'variables': class_vars,
                        'decorators': decorators,
                        'docstring': ast.get_docstring(node),
                        'bases': [_unparse(base) for base in node.bases]
                    })
                    self.current_class = old_class
                    self.generic_visit(node)

                def visit_FunctionDef(self, node):
                    if not self.current_class:
                        def _unparse(x):
                            if hasattr(ast, 'unparse'):
                                try:
                                    return ast.unparse(x)
                                except Exception:
                                    return str(x)
                            return str(x)
                        decorators = [_unparse(dec) for dec in node.decorator_list]
                        returns = _unparse(node.returns) if node.returns else None
                        structure['functions'].append({
                            'name': node.name, 'line': node.lineno,
                            'args': [arg.arg for arg in node.args.args],
                            'decorators': decorators,
                            'docstring': ast.get_docstring(node),
                            'returns': returns
                        })
                    self.generic_visit(node)

                def visit_Import(self, node):
                    for alias in node.names:
                        structure['imports'].append({
                            'name': alias.name, 'alias': alias.asname,
                            'line': node.lineno, 'type': 'import'
                        })

                def visit_ImportFrom(self, node):
                    for alias in node.names:
                        structure['imports'].append({
                            'name': f"{node.module}.{alias.name}" if node.module else alias.name,
                            'alias': alias.asname, 'line': node.lineno,
                            'type': 'from', 'module': node.module
                        })

                def visit_Assign(self, node):
                    if not self.current_class:
                        for t in node.targets:
                            if isinstance(t, ast.Name):
                                dest = structure['constants'] if t.id.isupper() else structure['variables']
                                val = "..."
                                try:
                                    if isinstance(node.value, ast.Constant):
                                        val = repr(node.value.value)
                                    elif isinstance(node.value, ast.List):
                                        val = f"[{len(node.value.elts)} items]"
                                    elif isinstance(node.value, ast.Tuple):
                                        val = f"({len(node.value.elts)} items)"
                                    elif isinstance(node.value, ast.Dict):
                                        val = f"{{{len(node.value.keys)} items}}"
                                except Exception:
                                    pass
                                dest.append({'name': t.id, 'line': node.lineno, 'value': val})
                    self.generic_visit(node)

            CodeVisitor().visit(tree)
            return structure
        except SyntaxError as e:
            return {
                'classes': [], 'functions': [], 'imports': [],
                'variables': [], 'decorators': [], 'constants': [],
                'error': str(e)
            }

class ReplaceSymbolDialog(QDialog):
    def __init__(self, kind: str, old_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Replace {kind} name")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"New name for {kind} '{old_name}':"))
        self.line_edit = QLineEdit(old_name)
        layout.addWidget(self.line_edit)
        btns = QDialogButtonBox()
        self.apply_btn = btns.addButton("Apply", QDialogButtonBox.AcceptRole)
        self.cancel_btn = btns.addButton(QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def value(self) -> str:
        return self.line_edit.text().strip()

class ReplaceBlockDialog(QDialog):
    def __init__(self, kind: str, old_name: str, old_code: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Replace {kind} Block")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Replace the entire {kind} '{old_name}' block:"))

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlainText(old_code)
        self.text_edit.setFont(QFont("Consolas", 10))
        # Simple highlighter
        PythonSyntaxHighlighter(self.text_edit.document(), theme="dark")

        layout.addWidget(self.text_edit)

        btns = QDialogButtonBox()
        self.apply_btn = btns.addButton("Replace", QDialogButtonBox.AcceptRole)
        self.cancel_btn = btns.addButton(QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def value(self) -> str:
        return self.text_edit.toPlainText()

class EnhancedCodeNavigationTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Code Structure")
        self.itemClicked.connect(self.on_item_clicked)
        self.editor = None
        self.setup_context_menu()

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self._highlight_color = QColor(120, 180, 255, 80)

        # Color cycling for right-click highlights
        self._highlight_colors = [
            QColor(255, 100, 100, 80),  # Red
            QColor(100, 255, 100, 80),  # Green
            QColor(100, 100, 255, 80),  # Blue
            QColor(255, 255, 100, 80),  # Yellow
            QColor(255, 100, 255, 80),  # Magenta
            QColor(100, 255, 255, 80),  # Cyan
            QColor(255, 165, 0, 80),    # Orange
            QColor(128, 0, 128, 80),    # Purple
        ]
        self._color_index = 0
        self._highlighted_blocks = {}  # item_id -> (start_line, end_line, color)

    def setup_context_menu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        item = self.itemAt(position)
        if item:
            menu = QMenu()
            jump_action = menu.addAction("Jump to Definition")
            jump_action.triggered.connect(lambda: self.on_item_clicked(item, 0))

            # Highlight structure block
            kind = item.data(0, Qt.UserRole + 2)
            if kind in ('class', 'function', 'method'):
                highlight_action = menu.addAction("Highlight Structure Block")
                highlight_action.triggered.connect(lambda: self._highlight_structure_block(item))

                # Remove highlight if present
                item_id = id(item)
                if item_id in self._highlighted_blocks:
                    remove_highlight_action = menu.addAction("Remove Highlight")
                    remove_highlight_action.triggered.connect(lambda: self._remove_structure_highlight(item))

            # Replace block action
            rename_action = menu.addAction("Replace Block...")
            rename_action.setEnabled(kind in ('class', 'function', 'method'))
            rename_action.triggered.connect(lambda: self._rename_item(item))

            menu.exec_(self.mapToGlobal(position))

    def _highlight_structure_block(self, item: QTreeWidgetItem):
        if not self.editor or not item:
            return
        kind = item.data(0, Qt.UserRole + 2)
        if kind not in ('class', 'function', 'method'):
            return

        start_line = int(item.data(0, Qt.UserRole))
        start, end = self.editor.compute_block_range(start_line)

        color = self._highlight_colors[self._color_index]
        self._color_index = (self._color_index + 1) % len(self._highlight_colors)

        item_id = id(item)
        self._highlighted_blocks[item_id] = (start, end, color)
        self._apply_all_highlights()

    def _remove_structure_highlight(self, item: QTreeWidgetItem):
        if not self.editor or not item:
            return
        item_id = id(item)
        if item_id in self._highlighted_blocks:
            del self._highlighted_blocks[item_id]
        self._apply_all_highlights()

    def _apply_all_highlights(self):
        if not self.editor:
            return
        self.editor._structure_selections = []
        for start, end, color in self._highlighted_blocks.values():
            doc_blocks = self.editor.blockCount()
            start_line = max(1, min(start, doc_blocks))
            end_line = max(start_line, min(end, doc_blocks))
            for ln in range(start_line, end_line + 1):
                block = self.editor.document().findBlockByNumber(ln - 1)
                if block.isValid():
                    cur = QTextCursor(block)
                    sel = QTextEdit.ExtraSelection()
                    sel.format.setBackground(color)
                    sel.format.setProperty(QTextFormat.FullWidthSelection, True)
                    sel.cursor = cur
                    self.editor._structure_selections.append(sel)
        self.editor.highlight_current_line()

    def clear_all_highlights(self):
        self._highlighted_blocks.clear()
        if self.editor:
            self.editor.clear_structure_highlight()

    def set_editor(self, editor):
        self.editor = editor
        if self.editor:
            self.editor.set_structure_highlight_color(self._highlight_color)

    def set_block_highlight_color(self, color: QColor):
        self._highlight_color = color
        if self.editor:
            self.editor.set_structure_highlight_color(color)

    def _highlight_item_block(self, item: QTreeWidgetItem):
        if not self.editor:
            return
        if not item or not item.data(0, Qt.UserRole):
            return
        kind = item.data(0, Qt.UserRole + 2)
        start_line = int(item.data(0, Qt.UserRole))

        self._apply_all_highlights()

        item_id = id(item)
        if item_id not in self._highlighted_blocks and kind in ('class', 'function', 'method'):
            start, end = self.editor.compute_block_range(start_line)
            doc_blocks = self.editor.blockCount()
            start_line = max(1, min(start, doc_blocks))
            end_line = max(start_line, min(end, doc_blocks))
            for ln in range(start_line, end_line + 1):
                block = self.editor.document().findBlockByNumber(ln - 1)
                if block.isValid():
                    cur = QTextCursor(block)
                    sel = QTextEdit.ExtraSelection()
                    sel.format.setBackground(self._highlight_color)
                    sel.format.setProperty(QTextFormat.FullWidthSelection, True)
                    sel.cursor = cur
                    self.editor._structure_selections.append(sel)
            self.editor.highlight_current_line()

    def _rename_item(self, item: QTreeWidgetItem):
        if not self.editor or not item:
            return
        kind = item.data(0, Qt.UserRole + 2)
        old_name = item.data(0, Qt.UserRole + 3)
        if kind not in ('class', 'function', 'method') or not old_name:
            return

        start_line = int(item.data(0, Qt.UserRole))
        start, end = self.editor.compute_block_range(start_line)
        old_code = self.editor.get_block_text(start, end)
        dlg = ReplaceBlockDialog(kind, old_name, old_code, self)
        if dlg.exec_() == QDialog.Accepted:
            new_code = dlg.value()
            if not new_code or new_code == old_code:
                return
            success = self.editor.replace_block_in_range(start, end, new_code)
            if success:
                self.editor.set_structure_highlight_range(start, start + len(new_code.splitlines()))
                cursor = self.editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, start - 1)
                self.editor.setTextCursor(cursor)
                self.editor.centerCursor()

    def update_structure(self, code_text: str):
        self.clear()
        structure = CodeStructureParser.parse_code(code_text)
        if 'error' in structure:
            error_item = QTreeWidgetItem(self, [f"Syntax Error: {structure['error']}"])
            error_item.setForeground(0, QBrush(QColor(255, 0, 0)))
            return

        # Order: Classes -> Functions -> Others (Constants, Variables, Imports)

        # classes
        if structure['classes']:
            classes_item = QTreeWidgetItem(self, ["🏛️ Classes"])
            classes_item.setExpanded(True)
            for cls in structure['classes']:
                class_name = f"🏛️ {cls['name']}"
                if cls.get('bases'):
                    class_name += f"({', '.join(cls['bases'])})"

                class_item = QTreeWidgetItem(classes_item, [class_name])
                class_item.setData(0, Qt.UserRole, cls['line'])
                class_item.setData(0, Qt.UserRole + 2, 'class')
                class_item.setData(0, Qt.UserRole + 3, cls['name'])

                # Methods
                for method in cls['methods']:
                    args_str = ', '.join(method.get('args', []))
                    method_display = f"🔧 {method['name']}({args_str})"
                    method_item = QTreeWidgetItem(class_item, [method_display])
                    method_item.setData(0, Qt.UserRole, method['line'])
                    method_item.setData(0, Qt.UserRole + 2, 'method')
                    method_item.setData(0, Qt.UserRole + 3, method['name'])

                # Class variables
                if cls['variables']:
                    vars_item = QTreeWidgetItem(class_item, ["📋 Class Variables"])
                    for var in cls['variables']:
                        var_display = f"{var['name']}"
                        vi = QTreeWidgetItem(vars_item, [var_display])
                        vi.setData(0, Qt.UserRole, var['line'])
                        vi.setData(0, Qt.UserRole + 2, 'class_variable')
                        vi.setData(0, Qt.UserRole + 3, var['name'])

        # functions
        if structure['functions']:
            functions_item = QTreeWidgetItem(self, ["⚙️ Functions"])
            functions_item.setExpanded(True)
            for func in structure['functions']:
                args_str = ', '.join(func.get('args', []))
                func_display = f"⚙️ {func['name']}({args_str})"
                func_item = QTreeWidgetItem(functions_item, [func_display])
                func_item.setData(0, Qt.UserRole, func['line'])
                func_item.setData(0, Qt.UserRole + 2, 'function')
                func_item.setData(0, Qt.UserRole + 3, func['name'])

        # constants
        if structure['constants']:
            constants_item = QTreeWidgetItem(self, ["🔢 Constants"])
            constants_item.setExpanded(True)
            for const in structure['constants']:
                display_name = f"{const['name']} = {const.get('value', '...')}"
                item = QTreeWidgetItem(constants_item, [display_name])
                item.setData(0, Qt.UserRole, const['line'])
                item.setData(0, Qt.UserRole + 2, 'constant')
                item.setData(0, Qt.UserRole + 3, const['name'])

        # variables
        if structure['variables']:
            variables_item = QTreeWidgetItem(self, ["📊 Variables"])
            variables_item.setExpanded(False)
            for var in structure['variables']:
                var_display = f"{var['name']}"
                vi = QTreeWidgetItem(variables_item, [var_display])
                vi.setData(0, Qt.UserRole, var['line'])
                vi.setData(0, Qt.UserRole + 2, 'variable')
                vi.setData(0, Qt.UserRole + 3, var['name'])

        # imports
        if structure['imports']:
            imports_item = QTreeWidgetItem(self, ["📦 Imports"])
            imports_item.setExpanded(True)
            for imp in structure['imports']:
                display_name = f"{imp['type']}: {imp['name']}"
                if imp.get('alias'):
                    display_name += f" as {imp['alias']}"
                item = QTreeWidgetItem(imports_item, [display_name])
                item.setData(0, Qt.UserRole, imp['line'])
                item.setData(0, Qt.UserRole + 2, 'import')
                item.setData(0, Qt.UserRole + 3, imp['name'])

    def search_items(self, text: str):
        self.search_timer.stop()
        self.search_text = text
        self.search_timer.start(300)

    def perform_search(self):
        if not hasattr(self, 'search_text') or not self.search_text:
            self.show_all_items()
            return
        text = self.search_text.lower()
        for i in range(self.topLevelItemCount()):
            self.hide_item_recursive(self.topLevelItem(i))
        for i in range(self.topLevelItemCount()):
            self.show_matching_items(self.topLevelItem(i), text)

    def hide_item_recursive(self, item):
        item.setHidden(True)
        for i in range(item.childCount()):
            self.hide_item_recursive(item.child(i))

    def show_matching_items(self, item, search_text):
        has_matching_child = False
        for i in range(item.childCount()):
            child = item.child(i)
            if self.show_matching_items(child, search_text):
                has_matching_child = True
        item_matches = search_text in item.text(0).lower()
        if item_matches or has_matching_child:
            item.setHidden(False)
            item.setExpanded(True)
            return True
        return False

    def show_all_items(self):
        for i in range(self.topLevelItemCount()):
            self.show_item_recursive(self.topLevelItem(i))

    def show_item_recursive(self, item):
        item.setHidden(False)
        for i in range(item.childCount()):
            self.show_item_recursive(item.child(i))

    def on_item_clicked(self, item, column):
        if self.editor and item.data(0, Qt.UserRole):
            line_number = int(item.data(0, Qt.UserRole))
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_number - 1)
            self.editor.setTextCursor(cursor)
            self.editor.centerCursor()
            self.editor.update_click_highlight()
            self._highlight_item_block(item)
            self.editor.setFocus()

# =============================
# Python Version Detector
# =============================

class PythonVersionDetector:
    @staticmethod
    def get_installed_versions() -> List[Dict]:
        versions = []
        checked_paths = set()
        python_names = ['python', 'python3', 'py']
        for major in range(3, 4):
            for minor in range(6, 14):
                python_names.extend([f'python{major}.{minor}', f'python{major}{minor}'])
        if platform.system() == "Windows":
            for major in range(3, 4):
                for minor in range(6, 14):
                    python_names.append(f'py -{major}.{minor}')

        common_paths = []
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Python\PythonCore")
                i = 0
                while True:
                    try:
                        version = winreg.EnumKey(key, i)
                        install_path_key = winreg.OpenKey(key, f"{version}\\InstallPath")
                        install_path = winreg.QueryValue(install_path_key, "")
                        common_paths.append(os.path.join(install_path, "python.exe"))
                        i += 1
                    except OSError:
                        break
            except Exception:
                pass
        else:
            common_paths.extend([
                '/usr/bin/python3', '/usr/local/bin/python3',
                '/opt/python/bin/python3', '/usr/bin/python', '/usr/local/bin/python'
            ])

        for candidate in list(dict.fromkeys(python_names + common_paths)):
            try:
                if candidate.startswith('py -'):
                    cmd = candidate.split() + ['--version']
                else:
                    cmd = [candidate, '--version']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
                if result.returncode == 0:
                    version_text = result.stdout.strip() or result.stderr.strip()
                    if 'Python' in version_text:
                        if candidate.startswith('py -'):
                            path_cmd = candidate.split() + ['-c', 'import sys; print(sys.executable)']
                        else:
                            path_cmd = [candidate, '-c', 'import sys; print(sys.executable)']
                        path_result = subprocess.run(path_cmd, capture_output=True, text=True, timeout=8)
                        executable_path = path_result.stdout.strip() if path_result.returncode == 0 else candidate
                        if executable_path in checked_paths:
                            continue
                        checked_paths.add(executable_path)
                        info_cmd = path_cmd[:-1] + ['-c', 'import sys,platform;'
                                                              'print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")\n'
                                                              'print(platform.architecture()[0])\n'
                                                              'print(sys.prefix)\n']
                        info_result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=8)
                        if info_result.returncode == 0:
                            lines = info_result.stdout.strip().splitlines()
                            version_number = lines[0] if len(lines) > 0 else "Unknown"
                            architecture = lines[1] if len(lines) > 1 else "Unknown"
                            prefix = lines[2] if len(lines) > 2 else "Unknown"
                        else:
                            version_number = "Unknown"; architecture = "Unknown"; prefix = "Unknown"

                        versions.append({
                            'name': candidate,
                            'version': version_text,
                            'path': executable_path,
                            'version_number': version_number,
                            'architecture': architecture,
                            'prefix': prefix
                        })
            except Exception:
                continue

        def version_key(v):
            try:
                return tuple(int(x) for x in v['version_number'].split('.'))
            except Exception:
                return (0, 0, 0)

        versions.sort(key=version_key, reverse=True)
        return versions

# =============================
# Enhanced Code Runner
# =============================

class EnhancedCodeRunner(QThread):
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    started_signal = pyqtSignal()

    def __init__(self, code: str, python_path: str, working_dir: str = None, parent=None):
        super().__init__(parent)
        self.code = code
        self.python_path = python_path
        self.working_dir = working_dir or os.getcwd()
        self.process: Optional[QProcess] = None
        self.temp_file: Optional[str] = None
        self._is_running = False

    def run(self):
        try:
            self._is_running = True
            self.started_signal.emit()
            import tempfile
            fd, self.temp_file = tempfile.mkstemp(suffix='.py')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(self.code)

            self.process = QProcess()
            self.process.setWorkingDirectory(self.working_dir)
            self.process.readyReadStandardOutput.connect(self.read_stdout)
            self.process.readyReadStandardError.connect(self.read_stderr)
            self.process.finished.connect(self.on_process_finished)  # correct signature below
            self.process.errorOccurred.connect(self.on_process_error)

            try:
                env = QProcessEnvironment.systemEnvironment()
                env.insert("PYTHONUNBUFFERED", "1")
                env.insert("PYTHONIOENCODING", "utf-8")
                self.process.setProcessEnvironment(env)
            except Exception:
                pass

            self.process.start(self.python_path, [self.temp_file])
            if not self.process.waitForStarted(5000):
                self.error_received.emit("Failed to start Python process")
                return

            # Block until finished (in this worker thread)
            self.process.waitForFinished(-1)
        except Exception as e:
            self.error_received.emit(f"Error running code: {str(e)}")
        finally:
            self.cleanup()

    def read_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
            if data:
                self.output_received.emit(data)

    def read_stderr(self):
        if self.process:
            data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
            if data:
                self.error_received.emit(data)

    def on_process_finished(self, exit_code: int, _status: QProcess.ExitStatus):
        self._is_running = False
        self.finished_signal.emit(int(exit_code))

    def on_process_error(self, _err):
        # Surface QProcess errors to the UI
        self.error_received.emit("Process error occurred.\n")

    def stop(self, force: bool = False):
        # Graceful terminate or force kill
        if self.process and self.process.state() == QProcess.Running:
            if force:
                self.process.kill()
                self.process.waitForFinished(3000)
            else:
                self.process.terminate()
                if not self.process.waitForFinished(2000):
                    self.process.kill()
                    self.process.waitForFinished(3000)
        self._is_running = False

    def force_stop(self):
        self.stop(force=True)

    def cleanup(self):
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.unlink(self.temp_file)
            except OSError:
                pass

    def is_running(self):
        return self._is_running

# =============================
# Simple PDB Debugger (stable)
# =============================

class SimplePdbDebugger(QObject):
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    started_signal = pyqtSignal()
    location_changed = pyqtSignal(int)  # 1-based line number

    def __init__(self, python_path: str, working_dir: str, parent=None):
        super().__init__(parent)
        self.python_path = python_path
        self.working_dir = working_dir
        self.process: Optional[QProcess] = None
        self.temp_file: Optional[str] = None
        self._running = False
        self._breakpoints: List[int] = []
        self._file_for_debug: Optional[str] = None
        self._prompt_seen = False
        # Fixed regex - removed KATEX artifacts, using simple parentheses
        self._loc_re = re.compile(r'>\s*(?P<file>.+)KATEX_INLINE_OPEN(?P<line>\d+)KATEX_INLINE_CLOSE\S*')
        self._prompt_re = re.compile(r'^KATEX_INLINE_OPENPdbKATEX_INLINE_CLOSE\s*$')

    def start(self, code: str, breakpoints: List[int]):
        try:
            import tempfile
            
            # Create a wrapper script that patches readline for Python 3.13 on Windows
            wrapper_code = """
import sys
import os

# Patch readline for Python 3.13 on Windows
try:
    import readline
    if not hasattr(readline, 'backend'):
        readline.backend = None
except ImportError:
    pass

# Now run the actual code with pdb
import pdb
import runpy

if __name__ == '__main__':
    target_file = sys.argv[1]
    sys.argv = [target_file]  # Reset argv for the target script
    
    # Set up pdb and run
    debugger = pdb.Pdb()
    try:
        debugger._run(runpy.run_path(target_file, run_name='__main__'))
    except SystemExit:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
        debugger.interaction(None, e)
"""
            
            # Create the target file with user code
            fd, self.temp_file = tempfile.mkstemp(suffix='.py')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            self._file_for_debug = os.path.normpath(self.temp_file)
            self._breakpoints = sorted(set(breakpoints or []))

            # Check Python version to decide whether to use wrapper
            python_version = self._get_python_version()
            use_wrapper = python_version and python_version >= (3, 13) and platform.system() == "Windows"

            self.process = QProcess()
            self.process.setWorkingDirectory(self.working_dir)

            try:
                env = QProcessEnvironment.systemEnvironment()
                env.insert("PYTHONIOENCODING", "utf-8")
                # Set environment variable to disable readline if possible
                env.insert("PYTHONDONTWRITEBYTECODE", "1")
                self.process.setProcessEnvironment(env)
            except Exception:
                pass

            self.process.readyReadStandardOutput.connect(self._read_stdout)
            self.process.readyReadStandardError.connect(self._read_stderr)
            self.process.finished.connect(self._finished)
            self.process.errorOccurred.connect(self._on_error)

            if use_wrapper:
                # For Python 3.13 on Windows, use wrapper script
                fd2, wrapper_file = tempfile.mkstemp(suffix='_wrapper.py')
                with os.fdopen(fd2, 'w', encoding='utf-8') as f:
                    f.write(wrapper_code)
                self._wrapper_file = wrapper_file
                args = [wrapper_file, self.temp_file]
            else:
                # For other versions, use standard pdb
                args = ['-m', 'pdb', self.temp_file]
                self._wrapper_file = None

            self.process.start(self.python_path, args)
            if not self.process.waitForStarted(5000):
                self.error_received.emit("Failed to start debugger.")
                return

            self._running = True
            self.started_signal.emit()
        except Exception as e:
            self.error_received.emit(f"Debugger start failed: {e}")

    def _get_python_version(self) -> Optional[Tuple[int, int]]:
        """Get the Python version of the interpreter"""
        try:
            result = subprocess.run(
                [self.python_path, '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split('.')
                if len(parts) >= 2:
                    return (int(parts[0]), int(parts[1]))
        except Exception:
            pass
        return None

    def _send(self, cmd: str):
        if self.process and self._running and self.process.state() == QProcess.Running:
            try:
                self.process.write((cmd + '\n').encode('utf-8'))
                self.process.flush()
            except Exception:
                pass

    def _set_breakpoints(self):
        for ln in self._breakpoints:
            self._send(f'break {self._file_for_debug}:{ln}')

    def _read_stdout(self):
        if not self.process:
            return
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        if not data:
            return
        self.output_received.emit(data)

        # Parse for prompt and location updates
        for line in data.splitlines():
            if self._prompt_re.search(line):
                if not self._prompt_seen:
                    self._prompt_seen = True
                    # When first prompt appears, set bps then continue
                    self._set_breakpoints()
                    self._send('continue')
            m = self._loc_re.match(line.strip())
            if m:
                file_path = os.path.normpath(m.group('file'))
                try:
                    line_no = int(m.group('line'))
                except Exception:
                    continue
                if self._file_for_debug and os.path.normcase(file_path) == os.path.normcase(self._file_for_debug):
                    self.location_changed.emit(line_no)

    def _read_stderr(self):
        if not self.process:
            return
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        if data:
            # Filter out the readline.backend error for Python 3.13
            lines = data.splitlines()
            filtered_lines = []
            skip_next = False
            for line in lines:
                if "readline.backend" in line or "AttributeError: module 'readline'" in line:
                    skip_next = True
                    continue
                if skip_next and ("File" in line or "Traceback" in line):
                    continue
                skip_next = False
                filtered_lines.append(line)
            
            if filtered_lines:
                filtered_data = '\n'.join(filtered_lines)
                if filtered_data.strip():
                    self.error_received.emit(filtered_data)

    def _finished(self, exit_code: int, _status):
        self._running = False
        self.finished_signal.emit(int(exit_code))
        self.cleanup()

    def _on_error(self, _err):
        self.error_received.emit("Debugger process error.\n")

    def stop(self):
        if self.process and self._running:
            self._send('quit')
            try:
                self.process.kill()
                self.process.waitForFinished(3000)
            except Exception:
                pass
        self._running = False
        self.cleanup()

    def cleanup(self):
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.unlink(self.temp_file)
            except OSError:
                pass
        if hasattr(self, '_wrapper_file') and self._wrapper_file and os.path.exists(self._wrapper_file):
            try:
                os.unlink(self._wrapper_file)
            except OSError:
                pass
        self.temp_file = None

    def is_running(self) -> bool:
        return self._running

    # Controls
    def cont(self): self._send('continue')
    def step_over(self): self._send('next')
    def step_into(self): self._send('step')
    def step_out(self): self._send('return')
    def send_command(self, cmd: str): self._send(cmd)

# =============================
# Find/Replace
# =============================

class AdvancedFindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setModal(False)
        self.editor: Optional[CodeEditor] = None
        self.last_search_pos = 0
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        find_group = QGroupBox("Find")
        find_layout = QGridLayout()
        self.find_line_edit = QLineEdit()
        self.find_line_edit.textChanged.connect(self.on_find_text_changed)
        find_layout.addWidget(QLabel("Find:"), 0, 0)
        find_layout.addWidget(self.find_line_edit, 0, 1)

        self.case_sensitive_cb = QCheckBox("Case sensitive")
        self.whole_word_cb = QCheckBox("Whole word")
        self.regex_cb = QCheckBox("Regular expression")
        self.wrap_around_cb = QCheckBox("Wrap around")
        self.wrap_around_cb.setChecked(True)

        find_layout.addWidget(self.case_sensitive_cb, 1, 0)
        find_layout.addWidget(self.whole_word_cb, 1, 1)
        find_layout.addWidget(self.regex_cb, 2, 0)
        find_layout.addWidget(self.wrap_around_cb, 2, 1)

        find_group.setLayout(find_layout)
        layout.addWidget(find_group)

        replace_group = QGroupBox("Replace")
        replace_layout = QGridLayout()
        self.replace_line_edit = QLineEdit()
        replace_layout.addWidget(QLabel("Replace:"), 0, 0)
        replace_layout.addWidget(self.replace_line_edit, 0, 1)
        replace_group.setLayout(replace_layout)
        layout.addWidget(replace_group)

        button_layout = QHBoxLayout()
        self.find_next_btn = QPushButton("Find Next")
        self.find_prev_btn = QPushButton("Find Previous")
        self.replace_btn = QPushButton("Replace")
        self.replace_all_btn = QPushButton("Replace All")
        self.count_btn = QPushButton("Count")

        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn.clicked.connect(self.find_previous)
        self.replace_btn.clicked.connect(self.replace_current)
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.count_btn.clicked.connect(self.count_matches)

        button_layout.addWidget(self.find_next_btn)
        button_layout.addWidget(self.find_prev_btn)
        button_layout.addWidget(self.replace_btn)
        button_layout.addWidget(self.replace_all_btn)
        button_layout.addWidget(self.count_btn)

        layout.addLayout(button_layout)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.find_line_edit.returnPressed.connect(self.find_next)
        self.replace_line_edit.returnPressed.connect(self.replace_current)

    def set_editor(self, editor):
        self.editor = editor
        if editor:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                self.find_line_edit.setText(cursor.selectedText())

    def on_find_text_changed(self):
        self.last_search_pos = 0
        if self.find_line_edit.text():
            self.highlight_all_matches()

    def get_search_flags(self):
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive_cb.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self.whole_word_cb.isChecked():
            flags |= QTextDocument.FindWholeWords
        return flags

    def find_next(self):
        if not self.editor or not self.find_line_edit.text():
            return False
        search_text = self.find_line_edit.text()
        flags = self.get_search_flags()
        cursor = self.editor.textCursor()

        if self.regex_cb.isChecked():
            found_cursor = self.find_with_regex(search_text, cursor.position(), True)
        else:
            found_cursor = self.editor.document().find(search_text, cursor, flags)

        if found_cursor.isNull() and self.wrap_around_cb.isChecked():
            cursor.movePosition(QTextCursor.Start)
            if self.regex_cb.isChecked():
                found_cursor = self.find_with_regex(search_text, 0, True)
            else:
                found_cursor = self.editor.document().find(search_text, cursor, flags)
        if not found_cursor.isNull():
            self.editor.setTextCursor(found_cursor)
            self.editor.update_click_highlight()
            self.status_label.setText("Found")
            return True
        else:
            self.status_label.setText("Not found")
            return False

    def find_previous(self):
        if not self.editor or not self.find_line_edit.text():
            return False
        search_text = self.find_line_edit.text()
        flags = self.get_search_flags() | QTextDocument.FindBackward
        cursor = self.editor.textCursor()

        if self.regex_cb.isChecked():
            found_cursor = self.find_with_regex(search_text, cursor.position(), False)
        else:
            found_cursor = self.editor.document().find(search_text, cursor, flags)

        if found_cursor.isNull() and self.wrap_around_cb.isChecked():
            cursor.movePosition(QTextCursor.End)
            if self.regex_cb.isChecked():
                found_cursor = self.find_with_regex(search_text, len(self.editor.toPlainText()), False)
            else:
                found_cursor = self.editor.document().find(search_text, cursor, flags)

        if not found_cursor.isNull():
            self.editor.setTextCursor(found_cursor)
            self.editor.update_click_highlight()
            self.status_label.setText("Found")
            return True
        else:
            self.status_label.setText("Not found")
            return False

    def find_with_regex(self, pattern: str, start_pos: int, forward: bool):
        try:
            flags = 0
            if not self.case_sensitive_cb.isChecked():
                flags |= re.IGNORECASE
            regex = re.compile(pattern, flags)
            text = self.editor.toPlainText()
            if forward:
                match = regex.search(text, start_pos)
            else:
                matches = list(regex.finditer(text[:start_pos]))
                match = matches[-1] if matches else None
            if match:
                cursor = QTextCursor(self.editor.document())
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), QTextCursor.KeepAnchor)
                return cursor
        except re.error as e:
            self.status_label.setText(f"Regex error: {str(e)}")
        return QTextCursor()

    def replace_current(self):
        if not self.editor:
            return
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_line_edit.text())
            self.find_next()

    def replace_all(self):
        if not self.editor or not self.find_line_edit.text():
            return
        find_text = self.find_line_edit.text()
        replace_text = self.replace_line_edit.text()
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        replacements = 0
        cursor.movePosition(QTextCursor.Start)
        while True:
            if self.regex_cb.isChecked():
                found_cursor = self.find_with_regex(find_text, cursor.position(), True)
            else:
                found_cursor = self.editor.document().find(find_text, cursor, self.get_search_flags())
            if found_cursor.isNull():
                break
            found_cursor.insertText(replace_text)
            cursor = found_cursor
            replacements += 1
        cursor.endEditBlock()
        self.status_label.setText(f"Replaced {replacements} occurrence(s)")

    def count_matches(self):
        if not self.editor or not self.find_line_edit.text():
            return
        find_text = self.find_line_edit.text()
        count = 0
        cursor = QTextCursor(self.editor.document())
        cursor.movePosition(QTextCursor.Start)
        while True:
            if self.regex_cb.isChecked():
                found_cursor = self.find_with_regex(find_text, cursor.position(), True)
            else:
                found_cursor = self.editor.document().find(find_text, cursor, self.get_search_flags())
            if found_cursor.isNull():
                break
            count += 1
            cursor = found_cursor
            cursor.movePosition(QTextCursor.NextCharacter)
        self.status_label.setText(f"Found {count} occurrence(s)")

    def highlight_all_matches(self):
        if not self.editor:
            return
        find_text = self.find_line_edit.text()
        if not find_text:
            self.editor.set_external_highlights([])
            return
        selections: List[QTextEdit.ExtraSelection] = []
        cursor = QTextCursor(self.editor.document())
        cursor.movePosition(QTextCursor.Start)
        while True:
            if self.regex_cb.isChecked():
                found_cursor = self.find_with_regex(find_text, cursor.position(), True)
            else:
                found_cursor = self.editor.document().find(find_text, cursor, self.get_search_flags())
            if found_cursor.isNull():
                break
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(255, 255, 0, 100))
            selection.cursor = found_cursor
            selections.append(selection)
            cursor = found_cursor
            cursor.movePosition(QTextCursor.NextCharacter)
        self.editor.set_external_highlights(selections)
# =============================
# Theme Manager
# =============================

class ThemeManager:
    THEMES = {
        'dark': {
            'name': 'Dark Theme',
            'background': '#2b2b2b',
            'foreground': '#ffffff',
            'selection': '#264F78',
            'line_highlight': '#3a3a3a',
            'line_numbers_bg': '#404040',
            'line_numbers_fg': '#888888',
            'word_click_bg': (38, 79, 120, 140)
        },
        'light': {
            'name': 'Light Theme',
            'background': '#ffffff',
            'foreground': '#000000',
            'selection': '#ADD6FF',
            'line_highlight': '#f0f0f0',
            'line_numbers_bg': '#f5f5f5',
            'line_numbers_fg': '#666666',
            'word_click_bg': (173, 214, 255, 160)
        },
        'monokai': {
            'name': 'Monokai',
            'background': '#272822',
            'foreground': '#f8f8f2',
            'selection': '#49483e',
            'line_highlight': '#3e3d32',
            'line_numbers_bg': '#3e3d32',
            'line_numbers_fg': '#90908a',
            'word_click_bg': (92, 99, 112, 150)
        }
    }

    @staticmethod
    def apply_theme(widget, theme_name):
        if theme_name not in ThemeManager.THEMES:
            return
        theme = ThemeManager.THEMES[theme_name]
        style = f"""
        QWidget {{
            background-color: {theme['background']};
            color: {theme['foreground']};
        }}
        QTextEdit, QPlainTextEdit {{
            background-color: {theme['background']};
            color: {theme['foreground']};
            selection-background-color: {theme['selection']};
        }}
        QTreeWidget {{
            background-color: {theme['background']};
            color: {theme['foreground']};
            alternate-background-color: {theme['line_highlight']};
        }}
        QMenuBar, QToolBar {{
            background-color: {theme['background']};
            color: {theme['foreground']};
        }}
        """
        widget.setStyleSheet(style)

    @staticmethod
    def structure_block_color(theme_name: str) -> QColor:
        theme = ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES['dark'])
        base = QColor(theme['selection'])
        c = QColor(base)
        c.setAlpha(70)  # low-opacity
        return c

    @staticmethod
    def word_click_color(theme_name: str) -> QColor:
        t = ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES['dark'])
        r, g, b, a = t['word_click_bg']
        return QColor(r, g, b, a)

# =============================
# Build Executable (PyInstaller)
# =============================

class BuildWorker(QObject):
    output = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, python_path: str, args: List[str], cwd: str):
        super().__init__()
        self.python_path = python_path
        self.args = args
        self.cwd = cwd
        self.process: Optional[QProcess] = None

    def start(self):
        self.process = QProcess()
        self.process.setWorkingDirectory(self.cwd)
        self.process.readyReadStandardOutput.connect(self._read_out)
        self.process.readyReadStandardError.connect(self._read_err)
        self.process.finished.connect(self._done)
        self.process.start(self.python_path, ['-m', 'PyInstaller'] + self.args)

    def _read_out(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        if data:
            self.output.emit(data)

    def _read_err(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        if data:
            self.output.emit(data)

    def _done(self, code, _status):
        self.finished.emit(int(code))


class BuildExecutableDialog(QDialog):
    def __init__(self, parent, python_path: str, script_path: Optional[str], work_dir: str):
        super().__init__(parent)
        self.setWindowTitle("Build Executable (PyInstaller)")
        self.setModal(False)  # modeless so it can be minimized
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.Window)

        self.python_path = python_path
        self.work_dir = work_dir
        self.worker: Optional[BuildWorker] = None

        # Inputs
        self.script_line = QLineEdit(script_path or "")
        self.name_line = QLineEdit("")

        self.onefile_cb = QCheckBox("One file (--onefile)")
        self.onedir_cb = QCheckBox("One directory (default)")
        self.onedir_cb.setChecked(True)

        self.console_cb = QCheckBox("Console (default)")
        self.windowed_cb = QCheckBox("Windowed/No console (--windowed)")

        self.noconfirm_cb = QCheckBox("No confirm (--noconfirm)")
        self.clean_cb = QCheckBox("Clean (--clean)")

        self.icon_line = QLineEdit("")
        self.icon_btn = QPushButton("Browse...")
        self.icon_btn.clicked.connect(self._browse_icon)

        self.upx_cb = QCheckBox("Use UPX")
        self.upx_line = QLineEdit("")
        self.upx_btn = QPushButton("UPX Dir...")
        self.upx_btn.clicked.connect(self._browse_upx)

        # Data files list widget and controls
        self.data_list = QListWidget()
        self.data_list.setMaximumHeight(100)
        self.add_data_btn = QPushButton("Add Data...")
        self.add_data_btn.clicked.connect(self._add_data)
        self.remove_data_btn = QPushButton("Remove Selected")
        self.remove_data_btn.clicked.connect(self._remove_data)
        self.clear_data_btn = QPushButton("Clear All")
        self.clear_data_btn.clicked.connect(self._clear_data)

        self.hidden_line = QLineEdit("")  # comma-separated
        self.paths_line = QLineEdit("")   # comma-separated

        # NEW: exclusions and output paths
        self.exclude_line = QLineEdit("")  # comma-separated modules
        self.dist_line = QLineEdit("")
        self.work_line = QLineEdit("")
        self.spec_line = QLineEdit("")
        self.dist_btn = QPushButton("Browse...")
        self.work_btn = QPushButton("Browse...")
        self.spec_btn = QPushButton("Browse...")
        self.dist_btn.clicked.connect(self._browse_dist)
        self.work_btn.clicked.connect(self._browse_work)
        self.spec_btn.clicked.connect(self._browse_spec)

        self.extra_args_line = QLineEdit("")

        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(180)

        self.build_btn = QPushButton("Build")
        self.build_btn.clicked.connect(self._build)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)

        self._layout()

    def _layout(self):
        layout = QVBoxLayout(self)
        grid = QGridLayout()

        # Script + name
        grid.addWidget(QLabel("Script:"), 0, 0)
        grid.addWidget(self.script_line, 0, 1)
        btn_browse_script = QPushButton("Browse...")
        btn_browse_script.clicked.connect(self._browse_script)
        grid.addWidget(btn_browse_script, 0, 2)

        grid.addWidget(QLabel("Name (--name):"), 1, 0)
        grid.addWidget(self.name_line, 1, 1)

        # Modes
        grid.addWidget(self.onefile_cb, 2, 0)
        grid.addWidget(self.onedir_cb, 2, 1)
        grid.addWidget(self.console_cb, 3, 0)
        grid.addWidget(self.windowed_cb, 3, 1)
        grid.addWidget(self.noconfirm_cb, 4, 0)
        grid.addWidget(self.clean_cb, 4, 1)

        # Icon
        grid.addWidget(QLabel("Icon (--icon):"), 5, 0)
        grid.addWidget(self.icon_line, 5, 1)
        grid.addWidget(self.icon_btn, 5, 2)

        # UPX
        grid.addWidget(self.upx_cb, 6, 0)
        grid.addWidget(self.upx_line, 6, 1)
        grid.addWidget(self.upx_btn, 6, 2)

        layout.addLayout(grid)
        
        # Data files section with list widget
        data_group = QGroupBox("Data Files (--add-data)")
        data_layout = QVBoxLayout()
        
        # List widget to show added data files
        data_layout.addWidget(QLabel("Added data files/folders:"))
        data_layout.addWidget(self.data_list)
        
        # Buttons for data management
        data_btn_layout = QHBoxLayout()
        data_btn_layout.addWidget(self.add_data_btn)
        data_btn_layout.addWidget(self.remove_data_btn)
        data_btn_layout.addWidget(self.clear_data_btn)
        data_btn_layout.addStretch()
        data_layout.addLayout(data_btn_layout)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # Hidden imports and paths
        grid2 = QGridLayout()
        grid2.addWidget(QLabel("Hidden imports (comma separated):"), 0, 0)
        grid2.addWidget(self.hidden_line, 0, 1, 1, 2)

        grid2.addWidget(QLabel("Paths (comma separated):"), 1, 0)
        grid2.addWidget(self.paths_line, 1, 1, 1, 2)

        # Exclusions and output paths
        grid2.addWidget(QLabel("Exclude modules (--exclude-module):"), 2, 0)
        grid2.addWidget(self.exclude_line, 2, 1, 1, 2)
        grid2.addWidget(QLabel("Comma separated (e.g. tkinter,tests)"), 3, 1, 1, 2)

        grid2.addWidget(QLabel("Dist path (--distpath):"), 4, 0)
        grid2.addWidget(self.dist_line, 4, 1)
        grid2.addWidget(self.dist_btn, 4, 2)

        grid2.addWidget(QLabel("Work path (--workpath):"), 5, 0)
        grid2.addWidget(self.work_line, 5, 1)
        grid2.addWidget(self.work_btn, 5, 2)

        grid2.addWidget(QLabel("Spec path (--specpath):"), 6, 0)
        grid2.addWidget(self.spec_line, 6, 1)
        grid2.addWidget(self.spec_btn, 6, 2)

        # Extra args
        grid2.addWidget(QLabel("Extra args:"), 7, 0)
        grid2.addWidget(self.extra_args_line, 7, 1, 1, 2)

        layout.addLayout(grid2)
        
        layout.addWidget(QLabel("Build Log:"))
        layout.addWidget(self.log_text)

        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(self.build_btn)
        btns.addWidget(self.close_btn)
        layout.addLayout(btns)

    def _add_data(self):
        """Open dialog to add data files or folders"""
        dialog = AddDataDialog(self.work_dir, self)
        if dialog.exec_() == QDialog.Accepted:
            source_path = dialog.source_path
            dest_folder = dialog.dest_folder
            if source_path:
                # Format: source_path|destination_folder
                if not dest_folder:
                    dest_folder = "."
                item_text = f"{source_path}|{dest_folder}"
                self.data_list.addItem(item_text)

    def _remove_data(self):
        """Remove selected data item from list"""
        current_item = self.data_list.currentItem()
        if current_item:
            self.data_list.takeItem(self.data_list.row(current_item))

    def _clear_data(self):
        """Clear all data items"""
        self.data_list.clear()

    def _browse_script(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Select script", self.work_dir, "Python Files (*.py);;All Files (*)")
        if fn:
            self.script_line.setText(fn)

    def _browse_icon(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Select icon", self.work_dir, "Icon Files (*.ico *.icns *.png);;All Files (*)")
        if fn:
            self.icon_line.setText(fn)

    def _browse_upx(self):
        d = QFileDialog.getExistingDirectory(self, "Select UPX directory", self.work_dir)
        if d:
            self.upx_line.setText(d)

    def _browse_dist(self):
        d = QFileDialog.getExistingDirectory(self, "Select dist path", self.work_dir)
        if d:
            self.dist_line.setText(d)

    def _browse_work(self):
        d = QFileDialog.getExistingDirectory(self, "Select work path", self.work_dir)
        if d:
            self.work_line.setText(d)

    def _browse_spec(self):
        d = QFileDialog.getExistingDirectory(self, "Select spec path", self.work_dir)
        if d:
            self.spec_line.setText(d)

    def _os_adddata_sep(self) -> str:
        return ';' if os.name == 'nt' else ':'

    def _build(self):
        script = self.script_line.text().strip()
        if not script or not os.path.exists(script):
            QMessageBox.warning(self, "Build", "Please select a valid script file.")
            return

        args: List[str] = []

        # mode
        if self.onefile_cb.isChecked():
            args.append('--onefile')
        if self.windowed_cb.isChecked():
            args.append('--windowed')
        elif self.console_cb.isChecked():
            args.append('--console')
        if self.noconfirm_cb.isChecked():
            args.append('--noconfirm')
        if self.clean_cb.isChecked():
            args.append('--clean')

        name = self.name_line.text().strip()
        if name:
            args += ['--name', name]

        icon = self.icon_line.text().strip()
        if icon:
            args += ['--icon', icon]

        if self.upx_cb.isChecked():
            upx_dir = self.upx_line.text().strip()
            if upx_dir:
                args += ['--upx-dir', upx_dir]

        # add-data from list widget
        sep = self._os_adddata_sep()
        for i in range(self.data_list.count()):
            item_text = self.data_list.item(i).text()
            if '|' in item_text:
                src, dst = item_text.split('|', 1)
                args += ['--add-data', f"{src}{sep}{dst}"]

        # hidden imports
        hidden = self.hidden_line.text().strip()
        if hidden:
            for item in [x.strip() for x in hidden.split(',') if x.strip()]:
                args += ['--hidden-import', item]

        # paths
        paths = self.paths_line.text().strip()
        if paths:
            for p in [x.strip() for x in paths.split(',') if x.strip()]:
                args += ['--paths', p]

        # excludes
        excl = self.exclude_line.text().strip()
        if excl:
            for item in [x.strip() for x in excl.split(',') if x.strip()]:
                args += ['--exclude-module', item]

        # output paths
        dist = self.dist_line.text().strip()
        if dist:
            args += ['--distpath', dist]
        work = self.work_line.text().strip()
        if work:
            args += ['--workpath', work]
        spec = self.spec_line.text().strip()
        if spec:
            args += ['--specpath', spec]

        # extra args
        extra = self.extra_args_line.text().strip()
        if extra:
            args += extra.split()

        args.append(script)

        self.log_text.clear()
        self.build_btn.setEnabled(False)

        if not self.python_path:
            QMessageBox.warning(self, "Build", "No Python interpreter selected.")
            self.build_btn.setEnabled(True)
            return

        # Optional: check PyInstaller
        try:
            chk = subprocess.run([self.python_path, '-m', 'PyInstaller', '--version'],
                                 capture_output=True, text=True, timeout=8)
            if chk.returncode != 0:
                QMessageBox.information(self, "PyInstaller",
                                        "PyInstaller not found. Install with:\n\npip install pyinstaller")
        except Exception:
            QMessageBox.information(self, "PyInstaller",
                                    "PyInstaller check failed. Make sure it is installed:\n\npip install pyinstaller")

        self.worker = BuildWorker(self.python_path, args, self.work_dir)
        self.worker.output.connect(self._append_log)
        self.worker.finished.connect(self._finish_build)
        self.worker.start()

    def _append_log(self, text: str):
        self.log_text.moveCursor(QTextCursor.End)
        self.log_text.insertPlainText(text)
        self.log_text.moveCursor(QTextCursor.End)

    def _finish_build(self, code: int):
        self._append_log(f"\n--- Build finished with exit code {code} ---\n")
        self.build_btn.setEnabled(True)
        if code == 0:
            QMessageBox.information(self, "Build", "Build completed successfully.\nCheck the 'dist' folder.")


# Add this new dialog class for adding data files
class AddDataDialog(QDialog):
    def __init__(self, work_dir: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Data File/Folder")
        self.setMinimumWidth(500)
        self.work_dir = work_dir
        self.source_path = ""
        self.dest_folder = "."
        
        layout = QVBoxLayout(self)
        
        # Source file/folder selection
        source_group = QGroupBox("Source")
        source_layout = QGridLayout()
        
        self.source_line = QLineEdit()
        self.source_line.setPlaceholderText("Select file or folder to include...")
        source_layout.addWidget(QLabel("Path:"), 0, 0)
        source_layout.addWidget(self.source_line, 0, 1)
        
        # Buttons for file and folder selection
        btn_layout = QHBoxLayout()
        self.browse_file_btn = QPushButton("Browse File...")
        self.browse_file_btn.clicked.connect(self._browse_file)
        self.browse_folder_btn = QPushButton("Browse Folder...")
        self.browse_folder_btn.clicked.connect(self._browse_folder)
        btn_layout.addWidget(self.browse_file_btn)
        btn_layout.addWidget(self.browse_folder_btn)
        source_layout.addLayout(btn_layout, 1, 1)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # Destination folder
        dest_group = QGroupBox("Destination")
        dest_layout = QGridLayout()
        
        self.dest_line = QLineEdit(".")
        self.dest_line.setPlaceholderText("Destination folder in the bundle (. for root)")
        dest_layout.addWidget(QLabel("Folder:"), 0, 0)
        dest_layout.addWidget(self.dest_line, 0, 1)
        dest_layout.addWidget(QLabel("Examples: . (root), data, assets/images"), 1, 1)
        
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
        
        # Preview
        self.preview_label = QLabel("Preview: ")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 5px; }")
        layout.addWidget(self.preview_label)
        
        # Update preview when text changes
        self.source_line.textChanged.connect(self._update_preview)
        self.dest_line.textChanged.connect(self._update_preview)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self._update_preview()
    
    def _browse_file(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Select file to include", self.work_dir, "All Files (*)")
        if fn:
            self.source_line.setText(fn)
    
    def _browse_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Select folder to include", self.work_dir)
        if d:
            self.source_line.setText(d)
    
    def _update_preview(self):
        source = self.source_line.text().strip()
        dest = self.dest_line.text().strip() or "."
        
        if source:
            # Show how it will appear in PyInstaller command
            sep = ';' if os.name == 'nt' else ':'
            preview = f"--add-data \"{source}{sep}{dest}\""
            self.preview_label.setText(f"Preview: {preview}")
        else:
            self.preview_label.setText("Preview: (select a file or folder)")
    
    def _accept(self):
        self.source_path = self.source_line.text().strip()
        self.dest_folder = self.dest_line.text().strip() or "."
        
        if not self.source_path:
            QMessageBox.warning(self, "Add Data", "Please select a file or folder to include.")
            return
        
        if not os.path.exists(self.source_path):
            QMessageBox.warning(self, "Add Data", "The selected path does not exist.")
            return
        
        self.accept()

# =============================
# Main IDE
# =============================

class ProfessionalPythonIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.current_working_dir = os.getcwd()
        self.code_runner: Optional[EnhancedCodeRunner] = None
        self.debugger: Optional[SimplePdbDebugger] = None
        # Use consistent app/org with QApplication to make settings stable across runs
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "PythonIDE", "Professional Python IDE")
        self.recent_files: List[str] = []
        self.current_theme = "dark"

        self.left_widget: Optional[QWidget] = None
        self.main_splitter: Optional[QSplitter] = None
        self.bottom_tabs: Optional[QTabWidget] = None
        self.symbol_combo: Optional[QComboBox] = None
        self.debug_output_text: Optional[QPlainTextEdit] = None
        self.debug_input_line: Optional[QLineEdit] = None
        self.debug_tab_index: int = -1
        self.build_tab_index: int = -1

        # Find/Replace created early to avoid timing issues
        self.find_replace_dialog = AdvancedFindReplaceDialog(self)

        self.setup_ui()
        self.setup_actions()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()
        self.load_settings()  # load after menus to refresh recent menu

        # Interpreter detection
        self.python_versions = PythonVersionDetector.get_installed_versions()
        self.populate_python_versions()

        self.setWindowTitle("Professional Python IDE")
        self.setGeometry(100, 100, 1600, 1000)

        ThemeManager.apply_theme(self, self.current_theme)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.main_splitter = QSplitter(Qt.Horizontal)

        # Left panel
        self.left_widget = QWidget()
        self.left_widget.setMaximumWidth(350)
        self.left_widget.setMinimumWidth(250)
        left_layout = QVBoxLayout(self.left_widget)

        version_group = QGroupBox("Python Environment")
        version_layout = QVBoxLayout()
        self.python_version_combo = QComboBox()
        self.python_version_combo.currentTextChanged.connect(self.on_python_version_changed)
        version_layout.addWidget(self.python_version_combo)
        self.python_info_label = QLabel("Select Python version")
        self.python_info_label.setWordWrap(True)
        self.python_info_label.setStyleSheet("color: gray; font-size: 10px;")
        version_layout.addWidget(self.python_info_label)
        version_group.setLayout(version_layout)
        left_layout.addWidget(version_group)

        # search + structure
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.structure_search = QLineEdit()
        self.structure_search.setPlaceholderText("Search code structure...")
        self.structure_search.textChanged.connect(self.on_structure_search)
        search_layout.addWidget(self.structure_search)
        left_layout.addLayout(search_layout)

        self.code_tree = EnhancedCodeNavigationTree()
        self.code_tree.set_block_highlight_color(ThemeManager.structure_block_color(self.current_theme))
        left_layout.addWidget(self.code_tree)

        self.main_splitter.addWidget(self.left_widget)

        # Center splitter
        center_splitter = QSplitter(Qt.Vertical)

        # Editor tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)

        self.new_file()
        center_splitter.addWidget(self.tab_widget)

        # Bottom tabs
        self.bottom_tabs = QTabWidget()
        self.bottom_tabs.setTabPosition(QTabWidget.South)

        # Output tab
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_controls = QHBoxLayout()
        self.run_button = QPushButton("▶ Run")
        self.run_button.setStyleSheet("QPushButton { background-color: #4CAF50; }")
        #self.stop_button = QPushButton("⏹ Stop")
        #self.stop_button.setEnabled(False)
        self.force_stop_button = QPushButton("⛔ Stop")
        self.force_stop_button.setEnabled(False)
        self.clear_output_button = QPushButton("🗑 Clear")
        self.run_button.clicked.connect(self.run_code)
        #self.stop_button.clicked.connect(lambda: self.stop_code(force=False))
        self.force_stop_button.clicked.connect(lambda: self.stop_code(force=True))
        self.clear_output_button.clicked.connect(self.clear_output)
        output_controls.addWidget(self.run_button)
        #output_controls.addWidget(self.stop_button)
        output_controls.addWidget(self.force_stop_button)
        output_controls.addWidget(self.clear_output_button)
        output_controls.addStretch()
        output_layout.addLayout(output_controls)

        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setMaximumHeight(300)
        output_layout.addWidget(self.output_text)
        self.bottom_tabs.addTab(output_widget, "Output")

        # Problems tab
        problems_widget = QListWidget()
        self.bottom_tabs.addTab(problems_widget, "Problems")

        # Debug tab
        debug_widget = QWidget()
        dlay = QVBoxLayout(debug_widget)
        self.debug_output_text = QPlainTextEdit()
        self.debug_output_text.setReadOnly(True)
        self.debug_output_text.setFont(QFont("Consolas", 10))
        dlay.addWidget(self.debug_output_text)
        row = QHBoxLayout()
        self.debug_input_line = QLineEdit()
        self.debug_input_line.setPlaceholderText("pdb command (e.g., p var, where, args, list)")
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_debug_command)
        self.debug_input_line.returnPressed.connect(self.send_debug_command)
        row.addWidget(self.debug_input_line)
        row.addWidget(send_btn)
        dlay.addLayout(row)
        self.debug_tab_index = self.bottom_tabs.addTab(debug_widget, "Debug")

        # Build tab
        build_widget = QPlainTextEdit()
        build_widget.setReadOnly(True)
        build_widget.setFont(QFont("Consolas", 10))
        self.build_tab_index = self.bottom_tabs.addTab(build_widget, "Build")

        center_splitter.addWidget(self.bottom_tabs)
        center_splitter.setSizes([700, 300])

        self.main_splitter.addWidget(center_splitter)
        self.main_splitter.setSizes([300, 1200])
        main_layout.addWidget(self.main_splitter)

        # Find/Replace dialog editor hookup for the initial tab
        self.find_replace_dialog.set_editor(self.get_current_editor())

    def setup_actions(self):
        # File
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.triggered.connect(self.new_file)
        self.open_action = QAction("&Open", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.triggered.connect(self.open_file)
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_file)
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.triggered.connect(self.close)

        # Edit
        self.undo_action = QAction("&Undo", self); self.undo_action.setShortcut(QKeySequence.Undo); self.undo_action.triggered.connect(self.undo)
        self.redo_action = QAction("&Redo", self); self.redo_action.setShortcut(QKeySequence.Redo); self.redo_action.triggered.connect(self.redo)
        self.cut_action = QAction("Cu&t", self); self.cut_action.setShortcut(QKeySequence.Cut); self.cut_action.triggered.connect(self.cut)
        self.copy_action = QAction("&Copy", self); self.copy_action.setShortcut(QKeySequence.Copy); self.copy_action.triggered.connect(self.copy)
        self.paste_action = QAction("&Paste", self); self.paste_action.setShortcut(QKeySequence.Paste); self.paste_action.triggered.connect(self.paste)
        self.find_action = QAction("&Find && Replace", self); self.find_action.setShortcut(QKeySequence.Find); self.find_action.triggered.connect(self.show_find_replace)

        # View
        self.toggle_tree_action = QAction("Toggle Code Structure", self)
        self.toggle_tree_action.setShortcut("Ctrl+Shift+E")
        self.toggle_tree_action.triggered.connect(self.toggle_code_tree)
        self.zoom_in_action = QAction("Zoom In", self); self.zoom_in_action.setShortcut(QKeySequence.ZoomIn); self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action = QAction("Zoom Out", self); self.zoom_out_action.setShortcut(QKeySequence.ZoomOut); self.zoom_out_action.triggered.connect(self.zoom_out)
        self.reset_zoom_action = QAction("Reset Zoom", self); self.reset_zoom_action.setShortcut("Ctrl+0"); self.reset_zoom_action.triggered.connect(self.reset_zoom)

        # Format
        self.format_code_action = QAction("Format Code", self)
        self.format_code_action.setShortcut("Ctrl+Shift+F")
        self.format_code_action.triggered.connect(self.format_code)
        self.comment_action = QAction("Comment/Uncomment", self)
        self.comment_action.setShortcut("Ctrl+/")
        self.comment_action.triggered.connect(self.toggle_comment)

        # Run
        self.run_action = QAction("&Run", self); self.run_action.setShortcut("F5"); self.run_action.triggered.connect(self.run_code)
        #self.stop_action = QAction("&Stop", self); self.stop_action.setShortcut("Shift+F5"); self.stop_action.triggered.connect(lambda: self.stop_code(False))
        self.force_stop_action = QAction("Stop", self); self.force_stop_action.setShortcut("Ctrl+Shift+F5"); self.force_stop_action.triggered.connect(lambda: self.stop_code(True))

        # Debug
        self.debug_start_action = QAction("Start Debugging", self); self.debug_start_action.setShortcut("F6"); self.debug_start_action.triggered.connect(self.start_debug)
        self.debug_continue_action = QAction("Continue", self); self.debug_continue_action.setShortcut("F8"); self.debug_continue_action.triggered.connect(self.debug_continue); self.debug_continue_action.setEnabled(False)
        self.debug_step_over_action = QAction("Step Over", self); self.debug_step_over_action.setShortcut("F10"); self.debug_step_over_action.triggered.connect(self.debug_step_over); self.debug_step_over_action.setEnabled(False)
        self.debug_step_into_action = QAction("Step Into", self); self.debug_step_into_action.setShortcut("F11"); self.debug_step_into_action.triggered.connect(self.debug_step_into); self.debug_step_into_action.setEnabled(False)
        self.debug_step_out_action = QAction("Step Out", self); self.debug_step_out_action.setShortcut("Shift+F11"); self.debug_step_out_action.triggered.connect(self.debug_step_out); self.debug_step_out_action.setEnabled(False)
        self.debug_stop_action = QAction("Stop Debugging", self); self.debug_stop_action.setShortcut("Shift+F6"); self.debug_stop_action.triggered.connect(self.stop_debug); self.debug_stop_action.setEnabled(False)
        self.toggle_breakpoint_action = QAction("Toggle Breakpoint", self); self.toggle_breakpoint_action.setShortcut("F9"); self.toggle_breakpoint_action.triggered.connect(self.toggle_breakpoint_at_cursor)

        # Tools
        self.preferences_action = QAction("&Preferences", self); self.preferences_action.triggered.connect(self.show_preferences)
        self.build_exe_action = QAction("Build Executable (PyInstaller)", self); self.build_exe_action.triggered.connect(self.build_executable)

        # Theme actions
        self.dark_theme_action = QAction("Dark Theme", self); self.dark_theme_action.setCheckable(True); self.dark_theme_action.triggered.connect(lambda: self.change_theme('dark'))
        self.light_theme_action = QAction("Light Theme", self); self.light_theme_action.setCheckable(True); self.light_theme_action.triggered.connect(lambda: self.change_theme('light'))
        self.monokai_theme_action = QAction("Monokai Theme", self); self.monokai_theme_action.setCheckable(True); self.monokai_theme_action.triggered.connect(lambda: self.change_theme('monokai'))

    def setup_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action); file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action); file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menubar.addMenu("&Edit")
        for a in (self.undo_action, self.redo_action): edit_menu.addAction(a)
        edit_menu.addSeparator()
        for a in (self.cut_action, self.copy_action, self.paste_action): edit_menu.addAction(a)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)
        edit_menu.addAction(self.comment_action)
        edit_menu.addAction(self.format_code_action)

        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.toggle_tree_action)
        view_menu.addSeparator()
        for a in (self.zoom_in_action, self.zoom_out_action, self.reset_zoom_action): view_menu.addAction(a)
        view_menu.addSeparator()
        theme_menu = view_menu.addMenu("Themes")
        theme_menu.addAction(self.dark_theme_action)
        theme_menu.addAction(self.light_theme_action)
        theme_menu.addAction(self.monokai_theme_action)

        run_menu = menubar.addMenu("&Run")
        run_menu.addAction(self.run_action)
        #run_menu.addAction(self.stop_action)
        run_menu.addAction(self.force_stop_action)

        debug_menu = menubar.addMenu("&Debug")
        for a in (self.debug_start_action, self.debug_continue_action, self.debug_step_over_action,
                  self.debug_step_into_action, self.debug_step_out_action, self.debug_stop_action,
                  self.toggle_breakpoint_action):
            debug_menu.addAction(a)

        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(self.build_exe_action)
        tools_menu.addAction(self.preferences_action)

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        for a in (self.new_action, self.open_action, self.save_action): toolbar.addAction(a)
        toolbar.addSeparator()
        for a in (self.undo_action, self.redo_action): toolbar.addAction(a)
        toolbar.addSeparator()
        for a in (self.run_action, self.force_stop_action): toolbar.addAction(a)
        toolbar.addSeparator()
        # Debug controls
        for a in (self.debug_start_action, self.debug_continue_action, self.debug_step_over_action,
                  self.debug_step_into_action, self.debug_step_out_action, self.debug_stop_action,
                  self.toggle_breakpoint_action):
            toolbar.addAction(a)
        toolbar.addSeparator()
        # Symbols quick-jump
        toolbar.addWidget(QLabel("Symbols: "))
        self.symbol_combo = QComboBox()
        self.symbol_combo.setMinimumWidth(260)
        self.symbol_combo.activated[int].connect(self.on_symbol_selected)
        toolbar.addWidget(self.symbol_combo)

    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        self.cursor_pos_label = QLabel("Line: 1, Column: 1")
        self.status_bar.addPermanentWidget(self.cursor_pos_label)
        self.encoding_label = QLabel("UTF-8")
        self.status_bar.addPermanentWidget(self.encoding_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def populate_python_versions(self):
        self.python_version_combo.clear()
        if not self.python_versions:
            self.python_version_combo.addItem("No Python found", None)
            self.python_info_label.setText("No Python installations detected")
            return
        for version in self.python_versions:
            display_text = f"{version['version']} ({version['architecture']})"
            self.python_version_combo.addItem(display_text, version)
        if self.python_versions:
            self.on_python_version_changed()

    def on_python_version_changed(self):
        version_data = self.python_version_combo.currentData()
        if version_data:
            info_text = f"Path: {version_data['path']}\nPrefix: {version_data['prefix']}"
            self.python_info_label.setText(info_text)
        else:
            self.python_info_label.setText("No Python selected")

    def on_structure_search(self, text):
        self.code_tree.search_items(text)

    def get_current_editor(self) -> Optional[CodeEditor]:
        current_widget = self.tab_widget.currentWidget()
        return current_widget if isinstance(current_widget, CodeEditor) else None

    def new_file(self):
        editor = CodeEditor()
        editor.set_click_highlight_color(ThemeManager.word_click_color(self.current_theme))
        self.code_tree.set_editor(editor)
        editor.textChanged.connect(self.text_changed)
        editor.cursorPositionChanged.connect(self.cursor_position_changed)
        editor.highlighter.theme = self.current_theme
        editor.highlighter.setup_highlighting_rules()
        index = self.tab_widget.addTab(editor, "Untitled")
        self.tab_widget.setCurrentIndex(index)
        if self.find_replace_dialog:
            self.find_replace_dialog.set_editor(editor)
        self.update_symbols_combo()
        return editor

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Python File", self.current_working_dir,
            "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.open_file_path(file_path)

    def open_file_path(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            for i in range(self.tab_widget.count()):
                w = self.tab_widget.widget(i)
                if hasattr(w, 'file_path') and w.file_path == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    return
            current_editor = self.get_current_editor()
            if (current_editor and current_editor.toPlainText() == "" and
                    self.tab_widget.tabText(self.tab_widget.currentIndex()) == "Untitled"):
                editor = current_editor
            else:
                editor = self.new_file()
            editor.setPlainText(content)
            editor.file_path = file_path
            file_name = os.path.basename(file_path)
            idx = self.tab_widget.currentIndex()
            self.tab_widget.setTabText(idx, file_name)
            self.tab_widget.setTabToolTip(idx, file_path)
            self.current_file = file_path
            self.current_working_dir = os.path.dirname(file_path)
            self.add_recent_file(file_path)
            self.status_label.setText(f"Opened: {file_name}")
            self.update_code_structure()
            self.update_symbols_combo()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")

    def save_file(self):
        editor = self.get_current_editor()
        if not editor:
            return
        if hasattr(editor, 'file_path') and getattr(editor, 'file_path'):
            self.save_to_file(editor.file_path, editor.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        editor = self.get_current_editor()
        if not editor:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Python File", self.current_working_dir,
            "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.save_to_file(file_path, editor.toPlainText())
            editor.file_path = file_path
            self.current_file = file_path
            self.current_working_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            index = self.tab_widget.currentIndex()
            self.tab_widget.setTabText(index, file_name)
            self.tab_widget.setTabToolTip(index, file_path)
            self.add_recent_file(file_path)

    def save_to_file(self, file_path: str, content: str):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_name = os.path.basename(file_path)
            self.status_label.setText(f"Saved: {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")

    def close_tab(self, index: int):
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            if widget:
                widget.deleteLater()
        else:
            editor = self.tab_widget.widget(index)
            if isinstance(editor, CodeEditor):
                editor.clear()
                if hasattr(editor, 'file_path'):
                    delattr(editor, 'file_path')
                self.tab_widget.setTabText(index, "Untitled")
                self.tab_widget.setTabToolTip(index, "")
                self.current_file = None
        self.update_symbols_combo()

    def tab_changed(self, index: int):
        editor = self.tab_widget.widget(index)
        if isinstance(editor, CodeEditor):
            self.code_tree.set_editor(editor)
            if self.find_replace_dialog:
                self.find_replace_dialog.set_editor(editor)
            self.update_code_structure()
            self.update_symbols_combo()
            if hasattr(editor, 'file_path'):
                self.current_file = editor.file_path
                self.current_working_dir = os.path.dirname(editor.file_path)
            else:
                self.current_file = None

    def text_changed(self):
        if hasattr(self, '_update_timer'):
            self._update_timer.stop()
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self.update_code_structure)
        self._update_timer.timeout.connect(self.update_symbols_combo)
        self._update_timer.start(500)

    def update_code_structure(self):
        editor = self.get_current_editor()
        if editor:
            self.code_tree.update_structure(editor.toPlainText())

    def update_symbols_combo(self):
        if not self.symbol_combo:
            return
        editor = self.get_current_editor()
        self.symbol_combo.blockSignals(True)
        self.symbol_combo.clear()
        if editor:
            structure = CodeStructureParser.parse_code(editor.toPlainText())
            items = []
            for cls in structure.get('classes', []):
                items.append(("Class", cls['name'], cls['line']))
                for m in cls.get('methods', []):
                    items.append(("Method", f"{cls['name']}.{m['name']}()", m['line']))
            for func in structure.get('functions', []):
                items.append(("Function", f"{func['name']}()", func['line']))
            for var in structure.get('variables', []):
                items.append(("Variable", var['name'], var['line']))
            for kind, label, line in items:
                self.symbol_combo.addItem(f"{kind}: {label}", line)
        self.symbol_combo.blockSignals(False)

    def on_symbol_selected(self, index: int):
        editor = self.get_current_editor()
        if not editor:
            return
        line_number = self.symbol_combo.itemData(index)
        if line_number:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, int(line_number) - 1)
            editor.setTextCursor(cursor)
            editor.centerCursor()
            editor.update_click_highlight()
            editor.setFocus()

    def cursor_position_changed(self):
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1
            self.cursor_pos_label.setText(f"Line: {line}, Column: {column}")

    def add_recent_file(self, file_path: str):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]
        self.update_recent_menu()
        self.save_settings()  # persist immediately

    def update_recent_menu(self):
        self.recent_menu.clear()
        valid_paths = [p for p in self.recent_files if p and os.path.exists(p)]
        if not valid_paths:
            action = self.recent_menu.addAction("No recent files")
            action.setEnabled(False)
            return
        for file_path in valid_paths:
            file_name = os.path.basename(file_path)
            action = self.recent_menu.addAction(file_name)
            action.setStatusTip(file_path)
            action.triggered.connect(lambda checked, path=file_path: self.open_file_path(path))

    def show_find_replace(self):
        editor = self.get_current_editor()
        if editor:
            self.find_replace_dialog.set_editor(editor)
            self.find_replace_dialog.show()
            self.find_replace_dialog.find_line_edit.setFocus()
            self.find_replace_dialog.find_line_edit.selectAll()

    def undo(self): 
        editor = self.get_current_editor()
        if editor: editor.undo()

    def redo(self): 
        editor = self.get_current_editor()
        if editor: editor.redo()

    def cut(self): 
        editor = self.get_current_editor()
        if editor: editor.cut()

    # FIXED: Ctrl+C copy for all widgets
    def copy(self):
        # Try to copy from the focused widget first
        focused_widget = QApplication.focusWidget()
        
        # Handle different widget types
        if isinstance(focused_widget, (QPlainTextEdit, QTextEdit, QLineEdit)):
            # These widgets have built-in copy functionality
            if hasattr(focused_widget, 'copy'):
                focused_widget.copy()
                return
        
        # Fall back to current editor
        editor = self.get_current_editor()
        if editor:
            editor.copy()

    def paste(self):
        editor = self.get_current_editor()
        if editor: editor.paste()

    def toggle_code_tree(self):
        if self.left_widget:
            self.left_widget.setVisible(not self.left_widget.isVisible())

    def zoom_in(self):
        for i in range(self.tab_widget.count()):
            w = self.tab_widget.widget(i)
            if isinstance(w, CodeEditor):
                w.zoom_in()

    def zoom_out(self):
        for i in range(self.tab_widget.count()):
            w = self.tab_widget.widget(i)
            if isinstance(w, CodeEditor):
                w.zoom_out()

    def reset_zoom(self):
        for i in range(self.tab_widget.count()):
            w = self.tab_widget.widget(i)
            if isinstance(w, CodeEditor):
                w.reset_zoom()

    def format_code(self):
        editor = self.get_current_editor()
        if not editor:
            return
        try:
            import autopep8
            code = editor.toPlainText()
            formatted_code = autopep8.fix_code(code)
            if formatted_code != code:
                cursor = editor.textCursor()
                cursor.beginEditBlock()
                cursor.select(QTextCursor.Document)
                cursor.insertText(formatted_code)
                cursor.endEditBlock()
                self.status_label.setText("Code formatted")
            else:
                self.status_label.setText("Code already formatted")
        except ImportError:
            QMessageBox.information(self, "Format Code", "autopep8 is not installed. Install it with:\npip install autopep8")

    def toggle_comment(self):
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        
        # Group comment operations into single undo step
        cursor.beginEditBlock()
        try:
            if not cursor.hasSelection():
                cursor.select(QTextCursor.LineUnderCursor)
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.StartOfLine)
            start_line = cursor.blockNumber()
            cursor.setPosition(end)
            end_line = cursor.blockNumber()
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.StartOfLine)
            for _ in range(start_line, end_line + 1):
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                line_text = cursor.selectedText()
                cursor.movePosition(QTextCursor.StartOfLine)
                if line_text.lstrip().startswith('#'):
                    pos = line_text.find('#')
                    cursor.setPosition(cursor.position() + pos)
                    cursor.deleteChar()
                    # remove a following space if present
                    if cursor.position() < len(editor.toPlainText()) and editor.toPlainText()[cursor.position()] == ' ':
                        cursor.deleteChar()
                else:
                    cursor.insertText('# ')
                if not cursor.movePosition(QTextCursor.Down):
                    break
        finally:
            cursor.endEditBlock()

    # Run
    def run_code(self):
        editor = self.get_current_editor()
        if not editor:
            return
        code = editor.toPlainText()
        if not code.strip():
            self.output_text.appendPlainText("No code to run.\n")
            return
        version_data = self.python_version_combo.currentData()
        if not version_data:
            self.output_text.appendPlainText("No Python interpreter selected.\n")
            return
        python_path = version_data['path']
        self.clear_output()
        self.output_text.appendPlainText(f"Running with {version_data['version']}...\n")
        self.output_text.appendPlainText(f"Working directory: {self.current_working_dir}\n")
        self.output_text.appendPlainText("-" * 60 + "\n")
        self.code_runner = EnhancedCodeRunner(code, python_path, self.current_working_dir, self)
        self.code_runner.output_received.connect(self.append_output)
        self.code_runner.error_received.connect(self.append_error)
        self.code_runner.finished_signal.connect(self.code_finished)
        self.code_runner.started_signal.connect(self.code_started)
        self.code_runner.start()

    def code_started(self):
        self.run_button.setEnabled(False)
        #self.stop_button.setEnabled(True)
        self.force_stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Running...")

    def stop_code(self, force: bool = False):
        if self.code_runner and self.code_runner.is_running():
            try:
                if force:
                    self.code_runner.force_stop()
                else:
                    self.code_runner.stop()
                self.append_output("\n--- Execution stopped by user ---\n" if not force else "\n--- Execution force-stopped by user ---\n")
            except Exception as e:
                self.append_error(f"Stop error: {e}\n")
        # Always reset UI state after stop/force-stop
        self.code_finished(exit_code=-1)

    def append_output(self, text: str):
        self.output_text.moveCursor(QTextCursor.End)
        self.output_text.insertPlainText(text)
        self.output_text.moveCursor(QTextCursor.End)

    def append_error(self, text: str):
        self.output_text.moveCursor(QTextCursor.End)
        self.output_text.insertPlainText(f"ERROR: {text}")
        self.output_text.moveCursor(QTextCursor.End)

    def code_finished(self, exit_code: int):
        self.run_button.setEnabled(True)
        #self.stop_button.setEnabled(False)
        self.force_stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        if exit_code == -1:
            status_msg = "Execution stopped"
        else:
            status_msg = "Execution completed successfully" if exit_code == 0 else f"Execution failed (exit code: {exit_code})"
        self.append_output(f"\n--- {status_msg} ---\n")
        self.status_label.setText(status_msg)
        # Clean up runner thread object
        if self.code_runner:
            try:
                if self.code_runner.isRunning():
                    self.code_runner.wait(100)  # don't block
            except Exception:
                pass
            self.code_runner = None

    def clear_output(self):
        self.output_text.clear()

    # Debug
    def start_debug(self):
        editor = self.get_current_editor()
        if not editor:
            QMessageBox.information(self, "Debug", "No active editor.")
            return

        # Already running?
        if getattr(self, 'debugger', None) and self.debugger.is_running():
            QMessageBox.information(self, "Debug", "Debugger is already running.")
            return

        # Pick Python interpreter
        version_data = self.python_version_combo.currentData() if hasattr(self, 'python_version_combo') else None
        python_path = version_data['path'] if version_data else sys.executable

        code = editor.toPlainText()
        if not code.strip():
            self._append_debug_text("No code to debug.\n")
            return

        # Clear previous execution highlight
        if hasattr(editor, 'set_execution_line'):
            editor.set_execution_line(None)

        # Create debugger
        self.debugger = SimplePdbDebugger(python_path, self.current_working_dir, self)

        # Wire signals
        self.debugger.output_received.connect(self._append_debug_text)
        self.debugger.error_received.connect(self._append_debug_text)
        self.debugger.finished_signal.connect(self._debug_finished)
        self.debugger.started_signal.connect(self._debug_started)
        self.debugger.location_changed.connect(self.on_debug_location)

        # Switch to Debug tab
        if hasattr(self, 'bottom_tabs') and self.bottom_tabs:
            for i in range(self.bottom_tabs.count()):
                if self.bottom_tabs.tabText(i) == "Debug":
                    self.bottom_tabs.setCurrentIndex(i)
                    break

        # Start with breakpoints
        bps = editor.get_breakpoints() if hasattr(editor, 'get_breakpoints') else []
        self.debugger.start(code, bps)

    # Helper: append to Debug output
    def _append_debug_text(self, text: str):
        if hasattr(self, 'debug_output_text') and self.debug_output_text:
            self.debug_output_text.moveCursor(QTextCursor.End)
            self.debug_output_text.insertPlainText(text)
            self.debug_output_text.moveCursor(QTextCursor.End)
        elif hasattr(self, 'output_text') and self.output_text:
            self.output_text.moveCursor(QTextCursor.End)
            self.output_text.insertPlainText(text)
            self.output_text.moveCursor(QTextCursor.End)
        else:
            print(text, end='')

    def _debug_started(self):
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText("Debugging...")
        self.enable_debug_controls(True)
        self._append_debug_text("Debugger started.\n")

    def _debug_finished(self, exit_code: int):
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText(f"Debug ended (exit code {exit_code}).")
        self._append_debug_text("\n--- Debugging finished ---\n")
        self.enable_debug_controls(False)
        editor = self.get_current_editor()
        if editor and hasattr(editor, 'set_execution_line'):
            editor.set_execution_line(None)

    def stop_debug(self):
        if self.debugger and self.debugger.is_running():
            self.debugger.stop()
            self.append_debug_output("\n--- Debugger stopped ---\n")
            self.enable_debug_controls(False)

    def debug_continue(self):
        if self.debugger and self.debugger.is_running():
            self.debugger.cont()

    def debug_step_over(self):
        if self.debugger and self.debugger.is_running():
            self.debugger.step_over()

    def debug_step_into(self):
        if self.debugger and self.debugger.is_running():
            self.debugger.step_into()

    def debug_step_out(self):
        if self.debugger and self.debugger.is_running():
            self.debugger.step_out()

    def send_debug_command(self):
        cmd = ""
        if hasattr(self, "debug_input_line") and self.debug_input_line:
            cmd = self.debug_input_line.text().strip()
        if not cmd:
            return

        if hasattr(self, "debugger") and self.debugger and self.debugger.is_running():
            try:
                self.debugger.send_command(cmd)
            except Exception as e:
                msg = f"Failed to send command: {e}\n"
                if hasattr(self, "debug_output_text") and self.debug_output_text:
                    self.debug_output_text.moveCursor(QTextCursor.End)
                    self.debug_output_text.insertPlainText(msg)
                    self.debug_output_text.moveCursor(QTextCursor.End)
                else:
                    print(msg, end="")
            else:
                if hasattr(self, "debug_output_text") and self.debug_output_text:
                    self.debug_output_text.moveCursor(QTextCursor.End)
                    self.debug_output_text.insertPlainText(f">>> {cmd}\n")
                    self.debug_output_text.moveCursor(QTextCursor.End)
            if hasattr(self, "debug_input_line") and self.debug_input_line:
                self.debug_input_line.clear()
        else:
            msg = "Debugger is not running.\n"
            if hasattr(self, "debug_output_text") and self.debug_output_text:
                self.debug_output_text.moveCursor(QTextCursor.End)
                self.debug_output_text.insertPlainText(msg)
                self.debug_output_text.moveCursor(QTextCursor.End)
            else:
                print(msg, end="")

    def enable_debug_controls(self, enabled: bool):
        self.debug_continue_action.setEnabled(enabled)
        self.debug_step_over_action.setEnabled(enabled)
        self.debug_step_into_action.setEnabled(enabled)
        self.debug_step_out_action.setEnabled(enabled)
        self.debug_stop_action.setEnabled(enabled)

    def append_debug_output(self, text: str):
        self.debug_output_text.moveCursor(QTextCursor.End)
        self.debug_output_text.insertPlainText(text)
        self.debug_output_text.moveCursor(QTextCursor.End)

    def on_debug_location(self, line: int):
        editor = self.get_current_editor()
        if editor:
            editor.set_execution_line(line)
            block = editor.document().findBlockByNumber(line - 1)
            if block.isValid():
                cur = editor.textCursor()
                cur.setPosition(block.position())
                editor.setTextCursor(cur)
                editor.centerCursor()

    def toggle_breakpoint_at_cursor(self):
        editor = self.get_current_editor()
        if not editor:
            return
        line = editor.textCursor().blockNumber() + 1
        editor.toggle_breakpoint(line)

    # Build exe
    def build_executable(self):
        editor = self.get_current_editor()
        current_path = getattr(editor, 'file_path', None) if editor else None
        version_data = self.python_version_combo.currentData()
        python_path = version_data['path'] if version_data else None

        if not hasattr(self, '_build_dialog') or self._build_dialog is None:
            self._build_dialog = BuildExecutableDialog(self, python_path, current_path, self.current_working_dir)
        else:
            self._build_dialog.python_path = python_path
            if current_path:
                self._build_dialog.script_line.setText(current_path)
            self._build_dialog.work_dir = self.current_working_dir

        self._build_dialog.show()
        self._build_dialog.raise_()
        self._build_dialog.activateWindow()

    # Theme & Prefs
    def change_theme(self, theme_name: str):
        self.current_theme = theme_name
        self.dark_theme_action.setChecked(theme_name == 'dark')
        self.light_theme_action.setChecked(theme_name == 'light')
        self.monokai_theme_action.setChecked(theme_name == 'monokai')
        ThemeManager.apply_theme(self, theme_name)
        if hasattr(self, 'code_tree') and self.code_tree:
            self.code_tree.set_block_highlight_color(ThemeManager.structure_block_color(theme_name))
        for i in range(self.tab_widget.count()):
            w = self.tab_widget.widget(i)
            if isinstance(w, CodeEditor):
                w.highlighter.theme = theme_name
                w.highlighter.setup_highlighting_rules()
                w.highlighter.rehighlight()
                w.set_click_highlight_color(ThemeManager.word_click_color(theme_name))

    def show_preferences(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Preferences")
        layout = QVBoxLayout(dialog)

        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        theme_combo = QComboBox()
        for tname, tdata in ThemeManager.THEMES.items():
            theme_combo.addItem(tdata['name'], tname)
        idx = theme_combo.findData(self.current_theme)
        if idx >= 0: theme_combo.setCurrentIndex(idx)
        theme_layout.addWidget(theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        font_group = QGroupBox("Font")
        font_layout = QVBoxLayout()
        font_button = QPushButton("Choose Font...")
        def choose_font():
            editor = self.get_current_editor()
            if editor:
                font, ok = QFontDialog.getFont(editor.font(), self)
                if ok:
                    for i in range(self.tab_widget.count()):
                        w = self.tab_widget.widget(i)
                        if isinstance(w, CodeEditor):
                            w.setFont(font)
                            w.update_line_number_area_width(0)
        font_button.clicked.connect(choose_font)
        font_layout.addWidget(font_button)
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            selected_theme = theme_combo.currentData()
            if selected_theme != self.current_theme:
                self.change_theme(selected_theme)

    # Settings
    def load_settings(self):
        geometry = self.settings.value("geometry")
        if geometry: self.restoreGeometry(geometry)
        state = self.settings.value("windowState")
        if state: self.restoreState(state)
        theme = self.settings.value("theme", "dark")
        self.change_theme(theme)
        # Ensure correct typing for recent files
        recent = self.settings.value("recentFiles", [], type=list)
        if isinstance(recent, list):
            self.recent_files = [str(p) for p in recent if p]
        working_dir = self.settings.value("workingDirectory")
        if working_dir and os.path.exists(str(working_dir)):
            self.current_working_dir = str(working_dir)
        # Refresh recent menu after load
        if hasattr(self, 'recent_menu'):
            self.update_recent_menu()

    def save_settings(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("theme", self.current_theme)
        self.settings.setValue("recentFiles", self.recent_files)
        self.settings.setValue("workingDirectory", self.current_working_dir)

    def closeEvent(self, event):
        # Stop processes safely
        if self.code_runner and self.code_runner.is_running():
            try:
                self.code_runner.stop()
            except Exception:
                pass
        if self.debugger and self.debugger.is_running():
            try:
                self.debugger.stop()
            except Exception:
                pass
        # simple unsaved prompt
        for i in range(self.tab_widget.count()):
            w = self.tab_widget.widget(i)
            if isinstance(w, CodeEditor):
                if w.toPlainText().strip():
                    reply = QMessageBox.question(
                        self, "Unsaved Changes",
                        "You may have unsaved changes. Are you sure you want to exit?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        event.ignore()
                        return
                    break
        self.save_settings()
        event.accept()

# =============================
# Main
# =============================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Professional Python IDE")
    app.setOrganizationName("PythonIDE")
    app.setApplicationVersion("2.1")
    app.setStyle('Fusion')
    ide = ProfessionalPythonIDE()
    ide.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()