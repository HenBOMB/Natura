from setuptools import setup, find_packages

setup(
    name            = 'natura',
    version         = '0.1',
    description     = 'Life Evolution of Augmenting Topologies',
    url             = '',
    author          = 'Henry Perazzo',
    author_email    = 'henbomb@hotmail.com',
    license         = 'MIT',
    packages        = ['natura'],
    # packages        = find_packages(exclude=['neat'], include=['natura', 'natura/reporters']),
    zip_safe        = False
)
