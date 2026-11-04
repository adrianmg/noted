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
      url "https://github.com/adrianmg/noted/releases/download/v1.9.0/noted-macos-universal.tar.gz"
      sha256 "270418f2d973b82535a3fcfbdbb8a8cee5986059fb1da4163cb8b975275e8469"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.0/noted-macos-universal.tar.gz"
      sha256 "270418f2d973b82535a3fcfbdbb8a8cee5986059fb1da4163cb8b975275e8469"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.0/noted-linux-x86_64.tar.gz"
      sha256 "7d036e82c9976d98df801d3518bda356f9c35170e32fcbd420aa5163dc57fd85"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.0/noted-linux-aarch64.tar.gz"
      sha256 "7462ac895cd8b13a41a23eb1024d97cbf7040cabd34e54648dce7ad1da14b18c"
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
