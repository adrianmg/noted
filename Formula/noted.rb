class Noted < Formula
  desc "Markdown notes in your terminal, as if they ran on MS-DOS"
  homepage "https://noted.computer"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  on_macos do
    # One binary for Apple silicon and Intel.
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.1/noted-macos-universal.tar.gz"
      sha256 "959667fbcd757ec9fca88e9554950a20b7d65683c6e5c1c6104172238b97a986"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.1/noted-macos-universal.tar.gz"
      sha256 "959667fbcd757ec9fca88e9554950a20b7d65683c6e5c1c6104172238b97a986"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.1/noted-linux-x86_64.tar.gz"
      sha256 "ede58fd4862dbd5f97f56d01addc376e109f22ca4a5857df4beca6afebbb5962"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.1/noted-linux-aarch64.tar.gz"
      sha256 "5cec4b2291c93035885c44d7b34f9f0d2590d48e86b8d05969d4b259b95947d7"
    end
  end

  def install
    bin.install "noted"
    prefix.install "noted.app" if OS.mac?
  end

  def caveats
    return unless OS.mac?

    <<~EOS
      To open noted from Spotlight, Raycast or Alfred, copy its app:
        cp -R #{opt_prefix}/noted.app ~/Applications/
    EOS
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/noted --version")
    assert_match "Markdown notes", shell_output("#{bin}/noted --help")
  end
end
