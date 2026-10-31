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
      url "https://github.com/adrianmg/noted/releases/download/v1.6.0/noted-macos-universal.tar.gz"
      sha256 "ad5e138c65b1f38fdc459d1461701e49743333e8896dbd0fdd576897c9f6cafa"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.6.0/noted-macos-universal.tar.gz"
      sha256 "ad5e138c65b1f38fdc459d1461701e49743333e8896dbd0fdd576897c9f6cafa"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.6.0/noted-linux-x86_64.tar.gz"
      sha256 "7223d74674871210b505a07a1ca1be75e15fbd9feaf785524f910f0e45e1c96d"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.6.0/noted-linux-aarch64.tar.gz"
      sha256 "64c390ee53816d4528beda3e013b3bf01559c16cab77f31ad9c8deac943cfd34"
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
