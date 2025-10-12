#!/usr/bin/env python3
"""
Test essential workflows with Act
Converted from test-workflows.sh to Python
"""

import subprocess
import sys
from pathlib import Path


class EssentialWorkflowTester:
    """Class to test essential workflows"""
    
    def __init__(self):
        self.workflows = [
            {
                "file": "ci.yml",
                "description": "CI workflow (lint & validate)",
                "dryrun": False
            },
            {
                "file": "security.yml", 
                "description": "Security workflow (Bandit & Safety)",
                "dryrun": False
            },
            {
                "file": "test.yml",
                "description": "Test workflow (unit & integration)",
                "dryrun": False
            },
            {
                "file": "codeql.yml",
                "description": "CodeQL workflow (security analysis)",
                "dryrun": False
            },
            {
                "file": "deploy.yml",
                "description": "Deploy workflow (staging & production)",
                "dryrun": True  # Deploy sempre em dry-run
            }
        ]
    
    def test_workflow(self, workflow_file: str, description: str, dryrun: bool = False) -> bool:
        """Test a single workflow"""
        icon = "🔒" if "security" in workflow_file else \
               "🧪" if "test" in workflow_file else \
               "🔍" if "codeql" in workflow_file else \
               "🚀" if "deploy" in workflow_file else "📋"
        
        print(f"{icon} Testando {description}...")
        
        try:
            cmd = [
                "act", "push",
                "-W", f".github/workflows/{workflow_file}",
                "--secret-file", ".secrets",
                "--env-file", ".env.act"
            ]
            
            if dryrun:
                cmd.append("--dryrun")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {workflow_file} executado com sucesso")
                return True
            else:
                print(f"❌ {workflow_file} falhou")
                if result.stderr:
                    print(f"Erro: {result.stderr[:200]}...")
                return False
                
        except FileNotFoundError:
            print("❌ Act não encontrado. Instale com:")
            print("   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash")
            return False
        except Exception as e:
            print(f"❌ Erro ao testar {workflow_file}: {e}")
            return False
    
    def run_tests(self):
        """Run all essential workflow tests"""
        print("🧪 Testando workflows essenciais com Act...")
        print("📁 Workflows ativos: CI, Security, Test, CodeQL, Deploy, Dependency Review")
        print("")
        
        passed = 0
        failed = 0
        
        for workflow in self.workflows:
            success = self.test_workflow(
                workflow["file"],
                workflow["description"],
                workflow["dryrun"]
            )
            
            if success:
                passed += 1
            else:
                failed += 1
            
            print("")
        
        print("✅ Testes concluídos!")
        print("ℹ️  Nota: Dependency Review roda apenas em pull_request")
        print("")
        print(f"📊 Resultados: {passed} passou(m), {failed} falhou(ram)")
        
        return failed == 0


def main():
    """Main function"""
    # Check if we're in the right directory
    if not Path(".github/workflows").exists():
        print("❌ Diretório .github/workflows não encontrado!")
        print("Execute este script na raiz do projeto.")
        sys.exit(1)
    
    tester = EssentialWorkflowTester()
    success = tester.run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()