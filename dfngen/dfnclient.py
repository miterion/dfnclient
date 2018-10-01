import json

import click
from termcolor import colored, cprint

from dfngen import openssl, soap

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command('create', help='Create a new certificate and signing request')
@click.argument('fqdn')
@click.option(
    '--pin',
    '-p',
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    type=str,
    help='Applicant code pin, will be prompted if not provided')
@click.option(
    '--applicant',
    '-a',
    type=str,
    help='Name of the applicant, defaults to value in config')
@click.option(
    '-c',
    '--config',
    type=click.File(),
    help='Path to config',
    show_default=True,
    default='~/.config/dfn-config.json',
)
def create_cert(fqdn, pin, applicant, config):
    print('Using config: ', colored('{}'.format(config), 'blue'))
    conf = parse_config(config)
    if not 'applicant' in conf:
        if applicant:
            conf['applicant'] = applicant
        else:
            conf['applicant'] = click.prompt(
                'No Applicant provided, please enter')
    conf['fqdn'] = fqdn
    conf['subject'] = conf['subject'].format(**conf)
    print('Generating certificate with the following values:\n')
    for key, value in conf.items():
        cprint('{}: {}'.format(key, value), 'yellow')
    click.confirm('Are these values correct?', default=True, abort=True)
    print('Generating certificate')
    req = openssl.gen_csr_with_new_cert(conf['fqdn'], conf['subject'])
    conf['pin'] = pin
    conf['altnames'] = [fqdn]
    conf['profile'] = 'Web Server'
    soap.submit_request(req, **conf)
    print('Generated pdf at:', colored('{}.pdf'.format(fqdn)))


@cli.command('csr', help='Generate a certificate for an existing certificate.')
@click.argument('fqdn')
@click.argument('path', type=click.Path(exists=True))
@click.option(
    '--applicant',
    '-a',
    type=str,
    help='Name of the applicant, defaults to value in config')
@click.option(
    '--pin',
    '-p',
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    type=str,
    help='Applicant code pin, will be prompted if not provided')
@click.option(
    '-c',
    '--config',
    type=click.File(),
    help='Path to config',
    show_default=True,
    default='~/.config/dfn-config.json',
)
def gen_existing(fqdn, pin, applicant, config, path):
    print('Using config: ', colored('{}'.format(config), 'blue'))
    conf = parse_config(config)
    if not 'applicant' in conf:
        if applicant:
            conf['applicant'] = applicant
        else:
            conf['applicant'] = click.prompt(
                'No Applicant provided, please enter')
    conf['fqdn'] = fqdn
    conf['subject'] = conf['subject'].format(**conf)
    print('Generating certificate signing request with the following values:\n')
    for key, value in conf.items():
        cprint('{}: {}'.format(key, value), 'yellow')
    click.confirm('Are these values correct?', default=True, abort=True)
    print('Generating certificate signing request')
    req = openssl.gen_csr_with_existing_cert(path, conf['fqdn'],
                                             conf['subject'])
    conf['pin'] = pin
    conf['altnames'] = [fqdn]
    conf['profile'] = 'Web Server'
    soap.submit_request(req, **conf)
    print('Generated pdf at:', colored('{}.pdf'.format(fqdn)))


@cli.command('generate_config', help='Prints an example config')
def create_config():
    print("""{ 
    "applicant": "John Doe",
    "mail": "john.doe@stud.example.com",
    "unit": "Department of Computer Science",
    "subject": "/C=DE/ST=Hessen/L=Darmstadt/O=TU/CN={fqdn}"
}
    """)


# Helper Methods


def parse_config(conf):
    return json.loads(conf.read())


if __name__ == '__main__':
    cli()
