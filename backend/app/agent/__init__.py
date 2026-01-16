"""Initialise le package de l'agent.

Ce fichier rend les composants principaux de l'agent, comme la fonction de création,
importables depuis d'autres parties de l'application.
"""
from .graph import app_graph

__all__ = ["app_graph"]