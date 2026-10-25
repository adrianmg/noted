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
      url "https://github.com/adrianmg/noted/releases/download/v1.0.0/noted-macos-universal.tar.gz"
      sha256 "8831f8c6df0ec6257cad0247d60f19a502290b1d87bfc6239a261bb930f26299"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.0.0/noted-macos-universal.tar.gz"
      sha256 "8831f8c6df0ec6257cad0247d60f19a502290b1d87bfc6239a261bb930f26299"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.0.0/noted-linux-x86_64.tar.gz"
      sha256 "5d232b468e927bd70714f6146f338983ada384f67d0fa03fe744e177fbf5d437"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.0.0/noted-linux-aarch64.tar.gz"
      sha256 "b70c4d6843529112be7acdc6ea0ff4fba4132c5e2e97723fb03c00af8a1120e7"
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
