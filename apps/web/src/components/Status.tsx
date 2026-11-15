import { useTranslation } from "react-i18next";

export function LoadingState(): JSX.Element {
  const { t } = useTranslation();
  return <p className="status">{t("status.loading")}</p>;
}

export function EmptyState(): JSX.Element {
  const { t } = useTranslation();
  return <p className="status">{t("status.empty")}</p>;
}

export function ErrorState({ message }: { message: string }): JSX.Element {
  return <p className="status error">{message}</p>;
}
