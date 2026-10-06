# 플랫폼별 연결 기록

이 파일에는 확인한 시점의 사실만 적습니다. 행동 규칙의 원본은 `../SKILL.md` 하나이고 이 파일은 그 규칙을 바꾸지 않습니다.
플랫폼이 바뀌면 공식 문서와 실제 환경을 다시 확인하고 이 표를 고칩니다(SKILL.md 10절).

확인일: 2026-10-06 · 확인한 환경: Windows 11, Claude Code 2.1.290, Codex CLI 0.152.0

| 환경 | 연결 방식 | 호출 | 확인 상태 |
| --- | --- | --- | --- |
| Claude Code | 네이티브 스킬 `~/.claude/skills/fun/SKILL.md` | `/fun` | 확인함. `claude -p "/fun"` 기록에 `<command-name>/fun</command-name>`이 남았고 스킬이 실행됨 |
| Claude Code | 명령 파일 `~/.claude/commands/Fun.md` (`claude-code/Fun.md`) → `fun` 스킬 호출 | `/Fun` | 확인함. 명령 파일이 없을 때 `/Fun` 단독 입력은 “명령이 없다”고 답함. 명령 파일을 넣은 뒤에는 `<command-name>/Fun</command-name>` → `fun` 스킬 호출로 이어짐 |
| Codex CLI·IDE | 네이티브 스킬 `~/.agents/skills/fun` | `$fun`, `$Fun`, 또는 `/skills`에서 선택 | `codex exec`에서 `$fun`, `$Fun` 둘 다 모델이 `SKILL.md`를 읽고 규칙대로 응답함. 대화형 화면(TUI)의 `$` 자동완성은 확인하지 않음. Codex는 스킬 이름으로 슬래시 명령을 만들지 않음(공식 문서) |
| Gemini CLI | 사용자 명령 어댑터 `gemini-cli/Fun.toml` (초안) | `/Fun` (파일 이름에서 나옴) | 시험한 PC에 Gemini CLI가 없어 설치·실행하지 않음. 형식만 공식 문서로 확인 |
| Grok | 확인한 등록 방식 없음 | 대화 약속만 | 스킬·코딩·일반 채팅 환경별 기능을 확인하지 못함 |
| 일반 채팅(ChatGPT, Gemini 앱, Grok 앱, claude.ai 등) | `SKILL.md` 본문을 프로젝트 지침이나 대화 첫 메시지로 넣음 | 그다음 `/Fun ...` 입력 | 대화 약속이며 시스템 명령 등록이 아님. 파일 쓰기가 없으면 명세 전체를 답으로 받아 직접 저장 |

## 알아 둘 점

- Claude Code는 스킬과 `.claude/commands/` 파일의 이름이 같으면 스킬을 실행합니다(공식 문서). `Fun.md`는 대문자 입력만 받아 `fun` 스킬로 넘기며 규칙은 담지 않습니다.
- `codex exec`로 시험할 때 Codex 설정 파일의 기본 모델이 계정에서 지원되지 않으면 스킬과 상관없이 첫 요청이 거부됩니다. 이때는 `-m`으로 쓸 수 있는 모델을 지정합니다.
- Git Bash에서 `claude -p "/fun"`처럼 `/`로 시작하는 인자를 넘기면 Git Bash가 경로(`C:/Program Files/Git/fun`)로 바꿔 버립니다. 시험은 PowerShell에서 합니다.

## Gemini CLI 어댑터 쓰는 법 (미검증)

`@{경로}` 파일 넣기는 작업 공간 안의 경로만 허용되므로, 공통 본문을 프로젝트 안으로 복사해야 합니다. 복사본은 이 저장소의 `SKILL.md`와 같아야 하며 따로 고치지 않습니다.

```bash
mkdir -p .gemini/commands .gemini/fun
cp <저장소>/fun/adapters/gemini-cli/Fun.toml .gemini/commands/Fun.toml
cp <저장소>/fun/SKILL.md .gemini/fun/SKILL.md
```

확인하지 못한 것: 명령 이름의 대소문자 구분(`/fun`으로도 불리는지), `@{}`가 `.gitignore`에 걸린 경로를 읽는지, 실제 실행 결과.

## 출처

- Claude Code 스킬: https://code.claude.com/docs/en/skills — 저장 위치, `name`이 명령 이름이 되는 규칙, 같은 이름이면 스킬이 실행됨, 세션 중 자동 반영
- Codex 스킬: https://learn.chatgpt.com/docs/build-skills — `$HOME/.agents/skills`, `$` 언급·`/skills`·ChatGPT `@`, `name`·`description` 필수
- Gemini CLI 사용자 명령: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/custom-commands.md — TOML `prompt`·`description`, 파일 이름이 명령 이름, `{{args}}`, `@{}`는 작업 공간 안만
