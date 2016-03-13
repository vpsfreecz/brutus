# Brutus - hosting management technology preview

## Testing the database from the command line

Add a test domain.

    ./brutus-db add examples/domain.yaml

Add a test account with mail configuration.

    ./brutus-db add examples/mailaccount.yaml

Check the contents of the database.

    ./brutus-db dump

## Generate testing configuration files

Generate text database files for Dovecot and Postfix.

    ./brutus-generate
