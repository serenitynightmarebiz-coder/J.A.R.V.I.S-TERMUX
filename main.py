"""Kivy UI for JARVIS — runs on Android (buildozer) and desktop (Kivy).

The agent logic is untouched: this file only wraps `Agent.ask()` in a
chat-bubble interface. On the phone it replaces the terminal REPL; on a
desktop it is the same app, so one codebase serves both.
"""

from __future__ import annotations

import os
import sys
from threading import Thread

# Make the repo root importable when running from buildozer's app dir.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from jarvis.agent import Agent
from jarvis.config import Config
from jarvis.memory import Memory


def _esc(text: str) -> str:
    """Kivy markup needs & and [ escaped."""
    return text.replace("&", "&amp;").replace("[", "&#91;").replace("]", "&#93;")


class Bubble(Label):
    """One chat message — gold for the user, cyan for JARVIS."""

    def __init__(self, text: str, who: str = "jarvis", **kwargs):
        super().__init__(**kwargs)
        self.who = who
        self.text = _esc(text)
        self.size_hint_y = None
        self.halign = "left"
        self.markup = True
        with self.canvas.before:
            if who == "you":
                Color(0.15, 0.15, 0.25, 1)
            else:
                Color(0.05, 0.15, 0.25, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_rect)
        self.bind(pos=self._update_rect)
        self.bind(texture_size=self._fit_height)

    def _fit_height(self, _instance, _value):
        self.height = self.texture_size[1] + dp(24)

    def _update_rect(self, _instance, _value):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ChatView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._layout = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            padding=dp(8),
        )
        self.add_widget(self._layout)
        self.bind(size=self._on_size)

    def _on_size(self, _instance, value):
        for child in self._layout.children:
            child.text_size = (value[0] - dp(40), None)

    def add_bubble(self, text: str, who: str = "jarvis"):
        bubble = Bubble(text, who)
        self._layout.add_widget(bubble)
        self.scroll_y = 0


class InputBar(BoxLayout):
    def __init__(self, on_send, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(56)
        self.on_send = on_send
        self.field = TextInput(
            hint_text="Ask JARVIS…",
            multiline=False,
            size_hint_x=0.8,
        )
        self.field.bind(on_text_validate=self._send)
        self.add_widget(self.field)
        send = Button(text="Send", size_hint_x=0.2)
        send.bind(on_press=self._send)
        self.add_widget(send)

    def _send(self, _instance):
        text = self.field.text.strip()
        if text:
            self.field.text = ""
            self.on_send(text)


class JarvisScreen(BoxLayout):
    def __init__(self, agent, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.agent = agent
        self.chat = ChatView()
        self.add_widget(self._header())
        self.add_widget(self.chat)
        self.add_widget(InputBar(self._ask))

    def _header(self) -> BoxLayout:
        bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48))
        bar.add_widget(Label(text="J.A.R.V.I.S.", font_size="20sp"))
        return bar

    def _ask(self, text: str):
        self.chat.add_bubble(text, "you")
        Thread(target=self._run, args=(text,), daemon=True).start()

    def _run(self, text: str):
        try:
            answer = self.agent.ask(text)
        except Exception as exc:  # noqa: BLE001 - keep the UI alive
            answer = f"I ran into a problem: {exc}"
        Clock.schedule_once(lambda _dt: self.chat.add_bubble(answer, "jarvis"))


class JarvisApp(App):
    title = "JARVIS"

    def build_config(self, config):
        config.setdefault("jarvis", "provider", "ollama")

    def build(self):
        cfg = Config.load()
        memory = Memory.load()
        agent = Agent(cfg, memory)
        return JarvisScreen(agent)


if __name__ == "__main__":
    JarvisApp().run()