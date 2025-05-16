#!/usr/bin/env python3
import unittest
import sys
import os
import argparse
import datetime
import glob
import subprocess
from pathlib import Path

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_config_loader import TestConfig
from init_test_db import initialize_test_database

def discover_tests(test_pattern=None):
    """Découvrir les tests à exécuter"""
    loader = unittest.TestLoader()
    
    # Si un motif spécifique est fourni, l'utiliser pour charger les tests
    if test_pattern:
        return loader.discover('.', pattern=f"test_{test_pattern}.py")
    
    # Sinon, charger tous les tests
    return loader.discover('.')

def generate_html_report(test_result, output_dir="results"):
    """Générer un rapport HTML des résultats des tests"""
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Générer le nom du fichier de rapport
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_report_{timestamp}.html")
    
    # Calculer les statistiques
    total_tests = test_result.testsRun
    success_count = total_tests - len(test_result.failures) - len(test_result.errors)
    success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
    
    # Générer le contenu HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rapport de Tests - {timestamp}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #444; margin-top: 30px; }}
            .summary {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            pre {{ background-color: #f8f8f8; padding: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>Rapport de Tests - Cyclist Performance API</h1>
        <div class="summary">
            <p>Date du rapport: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Tests exécutés: {total_tests}</p>
            <p>Succès: <span class="success">{success_count}</span></p>
            <p>Échecs: <span class="failure">{len(test_result.failures)}</span></p>
            <p>Erreurs: <span class="failure">{len(test_result.errors)}</span></p>
            <p>Taux de succès: <span class="{
                'success' if success_rate >= 90 else 'failure'
            }">{success_rate:.2f}%</span></p>
        </div>
    """
    
    # Ajouter les échecs de test
    if test_result.failures:
        html += """
        <h2>Échecs</h2>
        <table>
            <tr>
                <th>Test</th>
                <th>Message d'échec</th>
            </tr>
        """
        
        for test, failure in test_result.failures:
            html += f"""
            <tr>
                <td>{test}</td>
                <td><pre>{failure}</pre></td>
            </tr>
            """
        
        html += "</table>"
    
    # Ajouter les erreurs de test
    if test_result.errors:
        html += """
        <h2>Erreurs</h2>
        <table>
            <tr>
                <th>Test</th>
                <th>Message d'erreur</th>
            </tr>
        """
        
        for test, error in test_result.errors:
            html += f"""
            <tr>
                <td>{test}</td>
                <td><pre>{error}</pre></td>
            </tr>
            """
        
        html += "</table>"
    
    html += """
    </body>
    </html>
    """
    
    # Écrire le rapport dans un fichier
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Rapport HTML généré : {output_file}")
    return output_file

def run_tests(test_pattern=None, html_report=False, reset_db=False, verbosity=2):
    """Exécuter les tests avec unittest"""
    # Si demandé, réinitialiser la base de données de test
    if reset_db:
        initialize_test_database()
    
    # Découvrir et exécuter les tests
    test_suite = discover_tests(test_pattern)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(test_suite)
    
    # Si demandé, générer un rapport HTML
    if html_report:
        report_file = generate_html_report(result)
        
        # Ouvrir le rapport dans le navigateur par défaut
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(report_file)}", new=2)
        except:
            pass
    
    return result

def run_pytest(test_pattern=None, html_report=False, reset_db=False, verbosity=2):
    """Exécuter les tests avec pytest"""
    try:
        import pytest
    except ImportError:
        print("Module 'pytest' non trouvé. Installation...")
        subprocess.call([sys.executable, "-m", "pip", "install", "pytest", "pytest-html"])
        import pytest
    
    # Construire les arguments pytest
    pytest_args = []
    
    # Définir le niveau de verbosité
    if verbosity == 0:
        pytest_args.append("-q")
    elif verbosity == 2:
        pytest_args.append("-v")
    
    # Si un motif spécifique est fourni, l'utiliser
    if test_pattern:
        pytest_args.append(f"test_{test_pattern}.py")
    
    # Si demandé, générer un rapport HTML
    if html_report:
        os.makedirs("results", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"results/pytest_report_{timestamp}.html"
        pytest_args.extend(["--html", report_file, "--self-contained-html"])
    
    # Exécuter pytest avec les arguments
    retcode = pytest.main(pytest_args)
    
    # Si un rapport HTML a été généré, tenter de l'ouvrir
    if html_report:
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(report_file)}", new=2)
        except:
            pass
    
    return retcode

def list_tests():
    """Lister tous les tests disponibles"""
    test_files = glob.glob("test_*.py")
    
    if not test_files:
        print("Aucun fichier de test trouvé.")
        return
    
    print("\nTests disponibles :")
    print("-" * 50)
    
    for test_file in sorted(test_files):
        module_name = test_file[:-3]  # Supprimer l'extension .py
        print(f"- {module_name}")
        
        # Trouver les classes de test et les méthodes dans le fichier
        with open(test_file, 'r') as f:
            content = f.read()
            
        # Analyse simple pour trouver les classes et méthodes de test
        lines = content.split('\n')
        current_class = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('class ') and ('(unittest.TestCase)' in line or '(TestCase)' in line):
                current_class = line.split('class ')[1].split('(')[0].strip()
                print(f"  └── {current_class}")
            
            elif line.startswith('def test_') and current_class:
                method_name = line.split('def ')[1].split('(')[0].strip()
                print(f"      └── {method_name}")
    
    print("\nExécuter un test spécifique :")
    print("python run_tests.py --pattern auth  # Pour exécuter test_auth.py")
    print("python run_tests.py --pytest --pattern auth  # Pour exécuter avec pytest")
    print("python run_tests.py --list          # Pour lister tous les tests")
    print("python run_tests.py --all           # Pour exécuter tous les tests")
    print("-" * 50)

def run_coverage():
    """Exécuter les tests avec couverture de code"""
    try:
        import coverage
    except ImportError:
        print("Module 'coverage' non trouvé. Installation...")
        subprocess.call([sys.executable, "-m", "pip", "install", "coverage"])
        import coverage
    
    # Créer le répertoire de rapport s'il n'existe pas
    os.makedirs("coverage", exist_ok=True)
    
    # Lancer la mesure de couverture
    cov = coverage.Coverage(
        source=["utils", "views"],
        omit=["tests/*", "*/__pycache__/*", "*/venv/*"]
    )
    cov.start()
    
    # Exécuter tous les tests
    run_tests(test_pattern=None, html_report=False, reset_db=True, verbosity=0)
    
    # Arrêter la mesure et générer le rapport
    cov.stop()
    cov.save()
    
    # Rapport en ligne de commande
    print("\nRapport de couverture de code :")
    print("-" * 50)
    cov.report()
    
    # Rapport HTML
    cov.html_report(directory="coverage/html")
    
    print("\nRapport HTML généré dans 'coverage/html/index.html'")
    
    # Ouvrir le rapport dans le navigateur par défaut
    try:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath('coverage/html/index.html')}", new=2)
    except:
        pass

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Exécution des tests pour l'application Cyclist Performance")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pattern", help="Motif des tests à exécuter (ex: auth, api)")
    group.add_argument("--all", action="store_true", help="Exécuter tous les tests")
    group.add_argument("--list", action="store_true", help="Lister tous les tests disponibles")
    group.add_argument("--coverage", action="store_true", help="Exécuter les tests avec mesure de couverture")
    
    parser.add_argument("--html", action="store_true", help="Générer un rapport HTML")
    parser.add_argument("--reset-db", action="store_true", help="Réinitialiser la base de données de test")
    parser.add_argument("--verbosity", type=int, choices=[0, 1, 2], default=2, 
                        help="Niveau de détail des résultats des tests (0, 1 ou 2)")
    parser.add_argument("--pytest", action="store_true", help="Utiliser pytest au lieu de unittest")
    
    args = parser.parse_args()
    
    # Vérifier si nous sommes dans le répertoire de tests
    if not os.path.basename(os.getcwd()) == "tests":
        # Si nous sommes dans le répertoire parent, aller dans le répertoire de tests
        if os.path.isdir("tests"):
            os.chdir("tests")
        else:
            print("Erreur: Ce script doit être exécuté depuis le répertoire principal ou le répertoire 'tests'.")
            return 1
    
    if args.list:
        list_tests()
    elif args.coverage:
        run_coverage()
    else:
        # Exécuter les tests
        if args.pytest:
            run_pytest(
                test_pattern=args.pattern,
                html_report=args.html,
                reset_db=args.reset_db,
                verbosity=args.verbosity
            )
        else:
            run_tests(
                test_pattern=args.pattern,
                html_report=args.html,
                reset_db=args.reset_db,
                verbosity=args.verbosity
            )
    
    return 0

if __name__ == "__main__":
    sys.exit(main())