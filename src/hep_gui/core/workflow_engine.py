class WorkflowEngine:
    """Connects tabs together: Generation -> Analysis -> Plots."""

    def __init__(self, tabs, gen_tab, analysis_tab, plot_tab):
        self._tabs = tabs
        self._analysis_tab = analysis_tab
        self._plot_tab = plot_tab

        gen_tab.run_succeeded.connect(self._on_generation_done)
        analysis_tab.run_succeeded.connect(self._on_analysis_done)

    def _on_generation_done(self, hepmc_path):
        self._analysis_tab.set_hepmc_path(hepmc_path)
        self._tabs.setCurrentWidget(self._analysis_tab)

    def _on_analysis_done(self, yoda_path):
        self._plot_tab.load_yoda_path(yoda_path)
        self._tabs.setCurrentWidget(self._plot_tab)
