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
      url "https://github.com/adrianmg/noted/releases/download/v1.4.0/noted-macos-universal.tar.gz"
      sha256 "6df2b5c6e5f8b3a5174599cf9bde66f8f1bd68e7b156158b62c8c09c8bd5eed9"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.4.0/noted-macos-universal.tar.gz"
      sha256 "6df2b5c6e5f8b3a5174599cf9bde66f8f1bd68e7b156158b62c8c09c8bd5eed9"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.4.0/noted-linux-x86_64.tar.gz"
      sha256 "347a56013c682037ac8a4beb506c6364a249201ee1c9f97945bdc62bcded2177"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.4.0/noted-linux-aarch64.tar.gz"
      sha256 "2d512e9af94821b0687f8d9e4aab32e7f6ce7fdbc2e3018fa41704fe4e21d46a"
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
