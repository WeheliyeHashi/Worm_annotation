import setuptools

setuptools.setup(
    name='WormAnnotation',
    version='0.0.1',
    description='Tools to annotate worms',
    url='',
    author='Weheliye Hashi',
    author_email='w.weheliye@ic.ac.uk',
    license='MIT',
    packages=setuptools.find_packages(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "worm_annotator="
            + "WormAnnotation.worm_annotation"

        ]
    },
    )