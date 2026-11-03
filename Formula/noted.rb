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
      url "https://github.com/adrianmg/noted/releases/download/v1.8.0/noted-macos-universal.tar.gz"
      sha256 "af3121e50ff70b888bd6104317a7d110694bc2ae1d2105068f0213bd34bb335f"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.8.0/noted-macos-universal.tar.gz"
      sha256 "af3121e50ff70b888bd6104317a7d110694bc2ae1d2105068f0213bd34bb335f"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.8.0/noted-linux-x86_64.tar.gz"
      sha256 "a5224606dda0d716637a37233451b8920eb3fd281f990af38bc0c9bd22b0e77a"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.8.0/noted-linux-aarch64.tar.gz"
      sha256 "b629b56e7eb7cbc744ea56718202061e0dcd1451e2b51d869fa383b49533e536"
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
