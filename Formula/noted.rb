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
      url "https://github.com/adrianmg/noted/releases/download/v1.2.0/noted-macos-universal.tar.gz"
      sha256 "bb4411c428ea7dc91c0bf21ace323799a551495187de87f5dac19c072ff2c2d8"
    end
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.2.0/noted-macos-universal.tar.gz"
      sha256 "bb4411c428ea7dc91c0bf21ace323799a551495187de87f5dac19c072ff2c2d8"
    end
  end

  on_linux do
    # Static: any distribution.
    on_intel do
      url "https://github.com/adrianmg/noted/releases/download/v1.2.0/noted-linux-x86_64.tar.gz"
      sha256 "d558ba00e2e0b8bcf2333832e838b51fd99eb805f2cb35b036a3f46f90862284"
    end
    on_arm do
      url "https://github.com/adrianmg/noted/releases/download/v1.2.0/noted-linux-aarch64.tar.gz"
      sha256 "90997ae3c9e08ee3a47deec2463accce453a83b9ec89538983ed7681cf4d71ed"
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
