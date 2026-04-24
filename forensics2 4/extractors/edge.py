"""
EdgeExtractor — Microsoft Edge использует ту же структуру что и Chrome (Chromium),
поэтому просто наследуем ChromeExtractor с другим путём.
"""

from pathlib import Path
from core.paths import get_browser_paths
from extractors.chrome import ChromeExtractor


class EdgeExtractor(ChromeExtractor):
    name = "Edge"

    def __init__(self, base_path: Path = None):
        if base_path is None:
            base_path = get_browser_paths().get("edge", Path())
        super().__init__(base_path=base_path)
