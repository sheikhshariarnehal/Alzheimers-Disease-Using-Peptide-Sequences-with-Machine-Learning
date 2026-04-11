@echo off
echo ============================================================
echo Installing dependencies...
echo ============================================================
python -m pip install pandas numpy scikit-learn tensorflow matplotlib seaborn --quiet

echo.
echo ============================================================
echo Running Alzheimer's Peptide Detection Model...
echo ============================================================
python alzheimer_peptide_model.py

echo.
echo ============================================================
echo Complete! Check the models/ folder and model_comparison.png
echo ============================================================
pause
