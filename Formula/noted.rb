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
      url "https://github.com/adrianmg/noted/releases/download/v1.5.0/noted-macos-universal.tar.gz"
      sha256 "1754e2c73df43ddef6e02a1c41abf56f470abf9c515decedc18f9ff75af289df"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.5.0/noted-macos-universal.tar.gz"
      sha256 "1754e2c73df43ddef6e02a1c41abf56f470abf9c515decedc18f9ff75af289df"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.5.0/noted-linux-x86_64.tar.gz"
      sha256 "e5c924ec99692b3631875d429ed5285c01bbb86b07a7418da07bd73e4cd4def5"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.5.0/noted-linux-aarch64.tar.gz"
      sha256 "805d1890db8ba4ba5599b75b719fc8431a05f6762e6432ae92d4f9c3d55feb0c"
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
