import { Component, type ErrorInfo, type ReactNode } from "react";

interface ErrorBoundaryState {
  failed: boolean;
}

export class ErrorBoundary extends Component<
  { children: ReactNode },
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { failed: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Application rendering failure", error, info.componentStack);
  }

  render(): ReactNode {
    if (this.state.failed) {
      return (
        <main className="fatal-error" role="alert">
          <h1>Politiscales Analyser</h1>
          <p>Une erreur inattendue a interrompu l’affichage.</p>
          <button type="button" onClick={() => window.location.reload()}>
            Recharger l’application
          </button>
        </main>
      );
    }
    return this.props.children;
  }
}
