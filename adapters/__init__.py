"""Adapters — pure translators from the framework-agnostic package to each stack's format.

No LLM, no re-generation. Each adapter receives the domain oracle (verdict, well_formed)
so the adapters themselves stay generic — the refund rule lives in one place and is baked
identically into every stack's output. One core, one oracle, many stacks.
"""
