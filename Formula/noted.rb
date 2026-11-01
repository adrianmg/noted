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
      url "https://github.com/adrianmg/noted/releases/download/v1.7.0/noted-macos-universal.tar.gz"
      sha256 "48e847179e86799d37e3e68d8ea1cc82dce870d91a9e8075457a53845d1fd46f"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.7.0/noted-macos-universal.tar.gz"
      sha256 "48e847179e86799d37e3e68d8ea1cc82dce870d91a9e8075457a53845d1fd46f"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.7.0/noted-linux-x86_64.tar.gz"
      sha256 "cf03ba2a6751de89152e583b57d6c1b238af7db5f797a507d0fc31e87e068583"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.7.0/noted-linux-aarch64.tar.gz"
      sha256 "2b8752eadfea7fd8800f22171f31a378802e57fe0995585431ae2e2d8603807b"
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
