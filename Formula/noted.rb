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
      url "https://github.com/adrianmg/noted/releases/download/v1.9.3/noted-macos-universal.tar.gz"
      sha256 "b4eb22d6afba2816d0344c340983b48717286d279f6aebe6a59a1eedd0ed9e09"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.3/noted-macos-universal.tar.gz"
      sha256 "b4eb22d6afba2816d0344c340983b48717286d279f6aebe6a59a1eedd0ed9e09"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.3/noted-linux-x86_64.tar.gz"
      sha256 "7d79a27765b93f6cbb07a552355b1ea14e514d112005159a684d7320afa3571b"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.9.3/noted-linux-aarch64.tar.gz"
      sha256 "b0a5fbe97e59325c531f9338f0500244e40e84be00b8f7f52adb470c49032290"
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
