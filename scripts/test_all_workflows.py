#!/usr/bin/env python3
"""
Test all workflows with Act (dry-run)
Converted from test-all-workflows.sh to Python
"""

import subprocess
import sys
from pathlib import Path


class WorkflowTester:
    """Class to handle workflow testing with Act"""
    
    def __init__(self):
        self.workflows = [
            {
                "file": "ci.yml",
                "job": "validate",
                "description": "Lint, formatação e validação de código"
            },
            {
                "file": "test.yml", 
                "job": "",
                "description": "Testes unitários e integração com MongoDB"
            },
            {
                "file": "deploy.yml",
                "job": "",
                "description": "Deploy para staging e production"
            },
            {
                "file": "security.yml",
                "job": "",
                "description": "Scan de segurança (Bandit & Safety)"
            },
            {
                "file": "codeql.yml",
                "job": "",
                "description": "Análise de segurança do código"
            },
            {
                "file": "dependency-review.yml",
                "job": "",
                "description": "Análise de dependências em PRs"
            }
        ]
    
    def test_workflow(self, workflow_file: str, job: str, description: str) -> bool:
        """Test a single workflow"""
        print("━" * 40)
        print(f"📋 Testando: {workflow_file}")
        print(f"📝 Descrição: {description}")
        
        try:
            cmd = [
                "act", "push",
                "-W", f".github/workflows/{workflow_file}",
                "--secret-file", ".secrets",
                "--env-file", ".env.act",
                "--dryrun"
            ]
            
            if job:
                cmd.extend(["--job", job])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {workflow_file} passou no teste")
                return True
            else:
                print(f"❌ {workflow_file} falhou no teste")
                print(f"Erro: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ Act não encontrado. Instale com: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash")
            return False
        except Exception as e:
            print(f"❌ Erro ao testar {workflow_file}: {e}")
            return False
    
    def run_all_tests(self):
        """Run all workflow tests"""
        print("🧪 Testando todos os workflows com Act (dry-run)...")
        print(f"📁 Total de workflows: {len(self.workflows)} (CI, Test, Deploy, Security, CodeQL, Dependency Review)")
        print("")
        
        passed = 0
        failed = 0
        
        for workflow in self.workflows:
            success = self.test_workflow(
                workflow["file"],
                workflow["job"], 
                workflow["description"]
            )
            
            if success:
                passed += 1
            else:
                failed += 1
            
            print("")
        
        self.print_summary(passed, failed)
        return failed == 0
    
    def print_summary(self, passed: int, failed: int):
        """Print test summary"""
        print("━" * 40)
        print("🎯 Resumo dos testes concluído!")
        print("")
        print("📊 Workflows consolidados (de 12 para 6):")
        print("  ✅ ci.yml - CI principal")
        print("  ✅ test.yml - Testes automatizados")
        print("  ✅ deploy.yml - Deployment")
        print("  ✅ security.yml - Security scan")
        print("  ✅ codeql.yml - Code analysis")
        print("  ✅ dependency-review.yml - Dependency check")
        print("")
        print("🗑️  Removidos:")
        print("  ❌ ci-simple.yml (redundante)")
        print("  ❌ gemini-*.yml (5 workflows não utilizados)")
        print("")
        print(f"📈 Resultados: {passed} passou(m), {failed} falhou(ram)")


def main():
    """Main function"""
    # Check if we're in the right directory
    if not Path(".github/workflows").exists():
        print("❌ Diretório .github/workflows não encontrado!")
        print("Execute este script na raiz do projeto.")
        sys.exit(1)
    
    tester = WorkflowTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()