from pathlib import Path

from app.model import train_and_save


def main() -> None:
    here = Path(__file__).resolve().parent
    csv_path = here / "data" / "housing.csv"
    artifacts_dir = here / "artifacts"

    metadata = train_and_save(csv_path, artifacts_dir)
    m = metadata["metrics"]
    print("Training complete.")
    print(f"  rows            : {metadata['n_training_rows']}")
    print(f"  R^2 (train)     : {m['r2']:.4f}")
    print(f"  MAE             : {m['mae']:.2f}")
    print(f"  RMSE            : {m['rmse']:.2f}")
    print(f"  5-fold CV R^2   : {m['cv_r2_mean']:.4f} +/- {m['cv_r2_std']:.4f}")
    print(f"  artifacts in    : {artifacts_dir}")


if __name__ == "__main__":
    main()
