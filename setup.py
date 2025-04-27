from setuptools import setup, find_packages

setup(
    name="audio_upsampler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["numpy", "scipy", "soundfile"],
    entry_points={
        "console_scripts": [
            "upsample=audio_upsampler.main:main"
        ]
    },
)
