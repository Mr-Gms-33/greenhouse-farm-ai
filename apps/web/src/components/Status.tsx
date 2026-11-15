import { useTranslation } from "react-i18next";

export function LoadingState(): JSX.Element {
  const { t } = useTranslation();
  return (
    <div>
      <div className="loading-spinner" aria-hidden />
      <p className="status" style={{ textAlign: "center" }}>
        {t("status.loading")}
      </p>
    </div>
  );
}

export function EmptyState(): JSX.Element {
  const { t } = useTranslation();
  return (
    <div className="alert alert-info" role="status">
      {t("status.empty")}
    </div>
  );
}

export function ErrorState({ message }: { message: string }): JSX.Element {
  return (
    <div className="alert alert-danger" role="alert">
      {message}
    </div>
  );
}
