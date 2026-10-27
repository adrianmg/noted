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
      url "https://github.com/adrianmg/noted/releases/download/v1.1.0/noted-macos-universal.tar.gz"
      sha256 "295247a555804c0e05f7327d5876303c86e52b005a043dfbe4fd3ea2c4cbec62"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.1.0/noted-macos-universal.tar.gz"
      sha256 "295247a555804c0e05f7327d5876303c86e52b005a043dfbe4fd3ea2c4cbec62"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.1.0/noted-linux-x86_64.tar.gz"
      sha256 "a4ff31e9357b1bd1b4c27e3ca494d43c5267a1ec9849397a934cefca8ffa71cb"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.1.0/noted-linux-aarch64.tar.gz"
      sha256 "a8d0cf0b60daa13b287741662133420969838d2fb5489bbb6cae73fa9a02e4da"
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
