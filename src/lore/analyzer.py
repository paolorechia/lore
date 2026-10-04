from dataclasses import dataclass
from lore.providers.protocol import ProviderProtocol
from lore.file_system import FileSearcher

@dataclass
class FileAnalysis:
    file_path: str
    file_analysis: str

class FileAnalyzer:
    def __init__(self, provider: ProviderProtocol, file_searcher: FileSearcher):
        self._provider = provider
        self._file_searcher = file_searcher
        self._file_analyses: dict[str, FileAnalysis] = {}


    def analyze(self):
        self._file_searcher.find_files()
        files = self._file_searcher.get_files()

        for f in files.values():
            file_summary = self._provider.generate(
                f"I'm providing you a source code, summarize the intent and technological choices. Keep it short: {f}"
            )
            print(f.path, file_summary)
            self._file_analyses[f.path] = FileAnalysis(
                file_path=f.path,
                file_analysis=file_summary
            )


        response = self._provider.generate(
            f"Following this text, is a dump of a per file analysis. What key technological decisions were made in this project? {self._file_analyses}"
        )
        print(response)