# Annotating Assembly

Takes assembly code, matches it with opcodes and creates an annotated HTML file.

- hover opcodes for descriptions
- click labels to jump to branched-to routine
- creates a list of all labels
- dark mode, comments only mode

```shell
python convert.py code/POIZONE_10.txt opcodes/arm2.csv output/poizone.html
```

## Todo

- [ ] Graph or map that shows which routines branch to which labels
- [ ] Functionality to highlight and annotate code

## Imprint
The sample file *[POIZONE_10.txt](code/POIZONE_10.txt)* was written by Paolo Baerlocher and provided by him on [the games' archive repository](https://github.com/PaoloBaerlocher/Archimedes/blob/main/Poizone/POIZONE_10.txt).

Parts of the conversion script were prototyped with the help of [Claude](https://claude.ai). 

## License
This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
