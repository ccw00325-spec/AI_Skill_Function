"""SKILL.md 가 원문 명세(spec/Fun_skill_creation_prompt.md)에 충실한지 기계적으로 확인한다.

사용: py -I scripts/verify_skill.py   (저장소 뿌리에서)
표준 라이브러리만 쓴다. 실패 항목이 하나라도 있으면 종료 코드 1.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
spec = (ROOT / "spec" / "Fun_skill_creation_prompt.md").read_text(encoding="utf-8")
spec_lines = spec.split("\n")
skill_lines = skill.split("\n")

REQUEST = "‘비밀번호를 5번 틀리면 로그인을 막아줘’"
# build_skill.py 가 바꾼 원문 줄(제작자에게 하는 말 → 실행자에게 하는 말). README 에 공개되어 있다.
ALLOWED_CHANGED_PREFIXES = (
    "단순히 폼을 작성하는 스킬로 만들지 마라.",
    "프롬프트만으로 모든 환각이나 결함의 제거를",
    "공통 프롬프트를 읽은 이후 사용자의",
    "명세는 현재 사용자 프로젝트 폴더 안의",
    "## 12. 완성된 스킬의 수용 기준",
)

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def section(text_lines, start_heading, end_heading):
    s = text_lines.index(start_heading)
    e = text_lines.index(end_heading)
    return "\n".join(text_lines[s:e]).rstrip("\n")


# 1. frontmatter
m = re.match(r"^---\n(.*?)\n---\n", skill, re.S)
check("frontmatter 존재", m)
fm = m.group(1) if m else ""
check("name: fun", re.search(r"^name: fun$", fm, re.M))
spec_desc = re.search(r"^description: (.+)$", spec, re.M).group(1)
# 원문 13절 문장 뒤에 호출 표현 한 문장만 덧붙였다(사용자 요청: 대소문자·/·$ 모두 호출). README 에 공개.
check("description 이 원문 13절 문장으로 시작함", f"description: {spec_desc} " in fm)
keys = re.findall(r"^([A-Za-z_-]+):", fm, re.M)
check("frontmatter 는 name·description 만(플랫폼 전용 키 없음)", sorted(keys) == ["description", "name"], str(keys))

# 2. 예시 30개, 번호와 순서
heads = re.findall(r"^### 예시 (\d\d) — ", skill, re.M)
check("예시가 정확히 30개", len(heads) == 30, f"{len(heads)}개")
check("예시 번호 01~30 순서 고정", heads == [f"{i:02d}" for i in range(1, 31)])

# 3. 모든 예시가 같은 요청을 다룸
chunks = re.split(r"^### 예시 \d\d — ", skill, flags=re.M)[1:]
same = [i + 1 for i, c in enumerate(chunks) if REQUEST not in c.split("```")[0]]
check("30개 모두 같은 요청 ‘비밀번호를 5번 틀리면…’", not same, f"어긋난 예시: {same}")

# 4. 11절(예시 전체)이 원문과 글자 단위로 같음
sec11_spec = section(spec_lines, "## 11. 예시 적용 규칙 — 반드시 30개를 포함하라", "## 12. 완성된 스킬의 수용 기준")
sec11_skill = section(skill_lines, "## 11. 예시 적용 규칙 — 반드시 30개를 포함하라", "## 12. 자체 점검 기준 (원문 제목: 완성된 스킬의 수용 기준)")
check("11절(예시 30개 포함) 원문과 완전히 같음", sec11_spec == sec11_skill)

# 5. 예시 17 원문 요구·일곱 질문·두 Gherkin 블록
ex17 = chunks[16] if len(chunks) >= 17 else ""
q17 = [
    "- 다섯번째 실패라는 말은, 이미 네번 실패한 상태를 전제하는가?",
    "- 차단할 대상은 계정 ID 인가, IP 주소인가, 아니면 접속한 기기인가?",
    "- 실패 횟수는 일정 시간이 지나면 초기화되는가?",
    "- 계정은 몇분동안 잠기며, 화면에는 어떤 안내 문구를 보여줄 것인가?",
    "- 계정 잠금 메시지가 공격자에게 보안 정책의 단서를 제공하지는 않는가?",
    "- 관리자 계정에도 같은 정책을 적용할것인가?",
    "- 고객센터는 잠긴 계정을 어떤 절차와 증거를 기준으로 해제할것인가?",
]
check("예시 17 원문 요구", f"사용자 요구: **{REQUEST}**" in ex17)
check("예시 17 일곱 질문 그대로", all(q in ex17 for q in q17))
check("예시 17 원문 보존 블록(```text)", "```text\nFeature 로그인 차단 정책" in ex17)
check("예시 17 표준 Gherkin 블록(@illustration)", "```gherkin\n@illustration\nFeature: 로그인 차단 정책" in ex17)

# 6. 원문 1~9절·11~12절 줄이 빠짐없이 들어 있음(허용된 치환만 예외)
s1 = spec_lines.index("## 1. 목적과 기본 원칙")
s10 = spec_lines.index("## 10. 플랫폼 공통성과 /Fun 호출의 경계")
s11 = spec_lines.index("## 11. 예시 적용 규칙 — 반드시 30개를 포함하라")
s13 = spec_lines.index("## 13. 제작 결과의 출력")
skill_set = set(skill_lines)
missing = [
    l for l in spec_lines[s1:s10] + spec_lines[s11:s13]
    if l.strip() and l not in skill_set and not l.startswith(ALLOWED_CHANGED_PREFIXES)
]
check("원문 1~9·11·12절 줄 누락 없음(공개된 치환 5곳 제외)", not missing, "\n".join(missing[:5]))

# 7. 원문 10절 규칙 9개가 그대로 들어 있음
sec10_rules = [l for l in spec_lines[s10:s11] if l.startswith("- ")]
miss10 = [l for l in sec10_rules if l not in skill_set]
check(f"원문 10절 규칙 {len(sec10_rules)}개 그대로", not miss10, "\n".join(miss10))

# 8. '30분'이 예시 17·2절 7항·12절 밖에서 쓰이지 않음
allowed_30 = set()
for i, l in enumerate(skill_lines):
    if "30분" in l:
        allowed_30.add(i)
ex17_start = skill_lines.index("### 예시 17 — 사용자 제공 원문: 비밀번호 5회 실패 차단 정책")
ex17_end = skill_lines.index("### 예시 18 — 안내 문구와 정보 노출")
stray = [
    skill_lines[i] for i in allowed_30
    if not (ex17_start <= i < ex17_end)
    and not skill_lines[i].startswith("7. 예시에서 사용한 정책과 수치를")
    and not skill_lines[i].startswith(("6. 사용자 승인과 코드 관찰을", "- 사용자가 승인하지 않은 30분을", "6. 기존 코드의 30분 설정을"))
]
check("‘30분’이 사례·금지 규칙·점검 기준 밖에 없음", not stray, "\n".join(stray))

# 9. 12절 대표 확인 입력 7개
reps = re.findall(r"^[1-7]\. `/Fun|^[1-7]\. (질문 후|사용자가 대상|기존 코드의|파일 일부)", skill, re.M)
check("12절 대표 확인 입력 7개", len(reps) == 7, f"{len(reps)}개")

# 10. Gherkin 키워드 형식
feats = re.findall(r"^Feature:? ", skill, re.M)
bad_feats = [l for l in skill_lines if l.startswith("Feature ") and l != "Feature 로그인 차단 정책"]
check("Feature 콜론 누락은 예시 17 원문 보존 블록뿐", not bad_feats, str(bad_feats))

# 11. 8.1 빈칸 체크리스트(원문 이후 사용자 추가 요구)
check("8.1 빈칸 체크리스트 절이 8절과 9절 사이에 있음",
      "## 8.1 빈칸 체크리스트 (추가 요구, 2026-10-06)" in skill_lines
      and skill_lines.index("## 8.1 빈칸 체크리스트 (추가 요구, 2026-10-06)") < skill_lines.index("## 9. 구현 및 검증 규칙"))
check("8.1 표시 규칙(- [x]·- [ ]·✅·⬜·➖·❔) 정의", all(k in skill for k in ("`- [x]`", "`- [ ]`", "| ✅ |", "| ⬜ |", "| ➖ |", "| ❔ |")))
check("8.1 관찰 동작은 결정 칸을 체크하지 않는다는 규칙", "코드에서 관찰한 동작은 구현 칸에만 반영한다." in skill)
check("12.1 추가 점검 절", "### 12.1 추가 점검 (8.1 빈칸 체크리스트)" in skill_lines)

width = max(len(n) for n, _, _ in results)
fail = 0
for name, ok, detail in results:
    print(f"[{'통과' if ok else '실패'}] {name}")
    if not ok:
        fail += 1
        if detail:
            print("        " + detail.replace("\n", "\n        "))
print(f"\n{len(results) - fail}/{len(results)} 통과")
sys.exit(1 if fail else 0)
