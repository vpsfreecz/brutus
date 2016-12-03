# Brutus - hosting management technology preview

## Technology preview

During the first stage of developmnet the project will be kept as simple
as possible. Text formats available for human interaction is be YAML
or JSON. Machine communication is performed using JSON. Database backend
is based on the `shelve` python module.

## Supported software

  * Postfix 2.8

## Developers

Current status: The simplistic database backend works and we are currently
defining the requirements of the project, see `TODO.md`.

Developers are invited to help with the project, especially with the
following tasks:

  * Updating the `README.md` and `TODO.md` docs
  * Providing examples of data items in `examples/*.yaml` files
  * Working on service backends in `brutus/generate.py` or new modules
  * Creating JSON API based server and CLI and web clients
  * New ideas

## Testing and debugging

### Testing the database from the command line

Add a test domain.

    ./brutus-db add examples/domain.yaml

Add a test account with mail configuration.

    ./brutus-db add examples/mailaccount.yaml

Check the contents of the database.

    ./brutus-db dump

### Generate testing configuration files

Generate text database files for Dovecot and Postfix.

    ./brutus-generate

## License

We are currently publishing the software under a permissive 2-clause BSD
license.

## Community

The project was created by members of the vpsFree.cz project. You can
reach us in #vpsfree channel at IRC Freenode. All non-interactive project
communication occurs at GitHub using issues and pull requests.
