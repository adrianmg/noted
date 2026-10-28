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
      url "https://github.com/adrianmg/noted/releases/download/v1.3.0/noted-macos-universal.tar.gz"
      sha256 "1add8228bdac6d7b9198315e6ffce2f66ff42c7457c7aca5f203ae84c5782245"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.3.0/noted-macos-universal.tar.gz"
      sha256 "1add8228bdac6d7b9198315e6ffce2f66ff42c7457c7aca5f203ae84c5782245"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.3.0/noted-linux-x86_64.tar.gz"
      sha256 "2768196f5b182768751f68da5db1f773b9c31dce42647abf7f08b03a53b1969a"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.3.0/noted-linux-aarch64.tar.gz"
      sha256 "c5283bc1de4a4fc5cab43cb60310f1650f881d2cbcec54195c27f273b05451f3"
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
