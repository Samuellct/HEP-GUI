# HEP-GUI

Desktop application for managing the Monte Carlo event generation pipeline used in hep.

Wraps the MadGraph5_aMC@NLO + Pythia8 + Rivet workflow in a graphical interface so you can configure runs, monitor execution and visualize results without touching a terminal.

## Status

Pre-alpha

## Pipeline

```
MadGraph5 + Pythia8  -->  Rivet  -->  YODA histograms
    (event generation)    (analysis)   (visualization)
```

## License

MIT -- see [LICENSE](LICENSE)
