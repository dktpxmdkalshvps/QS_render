# Render Python 3.12 Fix

이번 수정본은 Render가 Python 3.14로 빌드하면서 SQLAlchemy/Alembic 실행 단계에서 발생한 타입 힌트 오류를 피하기 위해 Python 3.12.7을 명시합니다.

수정 사항:
- render.yaml: PYTHON_VERSION=3.12.7 추가
- runtime.txt: python-3.12.7 유지
- .python-version: 3.12.7 추가
- build.sh/start.sh: python --version 출력 추가

배포 후 로그에서 `Python 3.12.7` 또는 `Python 3.12.x`가 보이면 정상입니다.
