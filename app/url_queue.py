import os


class UrlQueue:
    def __init__(self, path):
        self.path = path

    def read(self):
        if not self.path.exists():
            return []
        lines = (line.strip() for line in self.path.read_text(encoding="utf-8").splitlines())
        return list(dict.fromkeys(line for line in lines if line))

    def append(self, urls):
        current = self.read()
        new_urls = [url for url in dict.fromkeys(urls) if url not in current]
        self._write(current + new_urls)
        return len(new_urls)

    def remove(self, url):
        self._write([item for item in self.read() if item != url])

    def _write(self, urls):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".tmp")
        content = "".join(f"{url}\n" for url in urls)
        temp_path.write_text(content, encoding="utf-8")
        os.replace(temp_path, self.path)
