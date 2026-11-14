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
      url "https://github.com/adrianmg/noted/releases/download/v1.9.2/noted-macos-universal.tar.gz"
      sha256 "10db9b22d065e49caba60c66b4da527253457721df012dbfc173c7f1a684db55"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.2/noted-macos-universal.tar.gz"
      sha256 "10db9b22d065e49caba60c66b4da527253457721df012dbfc173c7f1a684db55"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.2/noted-linux-x86_64.tar.gz"
      sha256 "65dadb341a8949e820536e6fa6395b5c6275ac45506f6009be22d9429954b97b"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.2/noted-linux-aarch64.tar.gz"
      sha256 "ba3e4ce8f1f63439b8f5992854f16d0d072567004714a5fed1fdc2d4060eeb3f"
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
