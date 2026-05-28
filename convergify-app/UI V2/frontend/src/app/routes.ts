import { createBrowserRouter } from "react-router";
import { RootLayout } from "./components/RootLayout";
import { AnalysisWizardLayout } from "./components/AnalysisWizardLayout";
import { JobDescriptionStep } from "./components/JobDescriptionStep";
import { ResumeUploadStep } from "./components/ResumeUploadStep";
import { ProcessingScreen } from "./components/ProcessingScreen";
import { MarketIntelligenceDashboard } from "./components/MarketIntelligenceDashboard";
import { StrategyDashboard } from "./components/StrategyDashboard";
import { StrategyLabArchive } from "./components/StrategyLabArchive";
import { OptimizationPage } from "./components/OptimizationPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: RootLayout,
    children: [
      {
        Component: AnalysisWizardLayout,
        children: [
          { index: true, Component: JobDescriptionStep },
          { path: "setup/target", Component: JobDescriptionStep },
          { path: "setup/resume", Component: ResumeUploadStep },
        ]
      },
      { path: "processing/:id", Component: ProcessingScreen },
      { path: "results/:id", Component: MarketIntelligenceDashboard },
      { path: "resume-analysis/:id", Component: StrategyDashboard },
      { path: "optimization/:id", Component: OptimizationPage },
      { path: "lab", Component: StrategyLabArchive },
    ],
  },
]);