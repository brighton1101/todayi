# todayi

## Currently this project is in its early stages. Remote functionality is weak, especially with regards to backing files up. Use at your own discretion.

## A cli that lets you keep track of what you do throughout the day with a single command:

```sh
🌴🌴🌴 todayi (master) $ todayi "Did something more with xyz and terraform" -t xyz terraform
```

This writes an entry to a backend (by default SQLite), with your entry's content `Fixed a bug with terraform/gcp setup` as well as two tags: `terraform` and `xyz`. Then, you can query for content using filters:

```sh
🌴🌴🌴 todayi (master) $ todayi show --with-tags "terraform,xyz" -a 12/21/2020
+-------------------------------------------+------------+----------------+
|               What was done:              |   When:    |     Tags:      |
+-------------------------------------------+------------+----------------+
| Did something more with xyz and terraform | 2020-12-21 | terraform, xyz |
+-------------------------------------------+------------+----------------+
```

You can also generate a markdown report with the following using the same filters:
```sh
🌴🌴🌴 todayi (master) $ todayi report md -o ~/Desktop/example.md --with-tags "terraform,xyz" -a 12/21/2020
```

Contents of the report:
```md
## 12-21-2020:
- 12:23 - Did something more with xyz and terraform - Tags: terraform, xyz

```

You can even post the report as a gist to Github
```sh
🌴🌴🌴 todayi (master) $ todayi report md -o example-report --with-tags "terraform,xyz" -a 12/21/2020 --gist --public
```
[See here](https://gist.github.com/brighton1101/798cabe484b7445cb9a2774408eb3961) for what was generated.


You can back it up to a configured 'remote' with the following (by default GCS)
```sh
🌴🌴🌴 todayi (master) $ todayi remote push
```

And you can pull from a remote just as easily...
```sh
🌴🌴🌴 todayi (master) $ todayi remote pull
```

Note that limited backup functionality is currently implemented for remotes using the `-B` or `--backup` flag

You can set configuration simply as well...
```sh
🌴🌴🌴 todayi (master) $ todayi config set github_auth_token "AUTH_TOKEN_HERE"
```

And then you can view that configuration easily.
```sh
🌴🌴🌴 todayi (master) $ todayi config get remote
gcs
```

### Available Backend Implementations:
- `sqlite`

### Available Remote Implementations:
- `gcs`
- `git` (experimental)

### Available Report Formats:
- `md`
- `csv`
- `gist` (which will post either a markdown or csv report, depending on what is specified)

Note that all of the above is extremely easy to add on to

### Development:
- `more to come`
