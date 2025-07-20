# 고민한 포인트 및 설계

## 1. 스케쥴의 구성

- `Schedule` 모델은 반복 일정의 기준 시간(`time`), 시작일(`start_datetime`), 종료일(`end_datetime`)을 포함한다.
- 요일 반복은 `ScheduleDay` 모델로 분리하여 관리하며, 정수 기반 `enum Weekday`를 활용해 일관성 있게 표현하였다.

## 2. 쉬어가기(Exclusion) 처리

- 특정 날짜에 일정을 건너뛰기 위한 구조로 `ScheduleExclusion` 모델을 정의하였다.
- `Schedule`과의 관계를 통해 쉬어가는 날짜를 명시적으로 연결할 수 있으며, 기존 반복 구조는 그대로 유지된다.

## 3. 하루 시간 변경(Time Modification) 처리

- 처음 하루의 시간 변경 요청 시 기존 `Schedule`을 종료시키고, 새 일정을 새로 생성하는 방식으로 처리하였다.
- 하지만 이 방식은 쉬어가기 처리와 충돌하였다. 새로운 일정을 생성하게 되면 **그 날 하루가 기존 `Schedule`과의 연결이 끊기므로, 해당 날짜에 설정된 쉬어가기 정보가
  반영되지 않게 된다.**
- 다시 말해, 단순히 시간을 변경하고 싶은 것임에도 새로운 일정이 생성되면 **그날의 모든 시간 설정과 예외 로직이 무효화**되는 문제가 발생한다.
- 따라서 설계를 변경하여, 시간 변경 역시 기존 `Schedule`의 일부로 간주하고 `ScheduleTimeModification` 모델을 통해 개별 날짜에 대한 시간만
  예외적으로 관리하는 방식으로 전환하였다.
- 이로 인해 시간 변경 역시 "일정에 귀속되어 처리되는 것"으로 해석되며, 쉬어가기와 공존할 수 있다.

## 4. 전체 스케쥴 변경 처리

- 전체 반복 시간이나 요일을 바꾸는 경우에는 기존 `Schedule`을 만료(`end_datetime` 설정)시키고, 새로운 `Schedule` 객체를 생성하여 이력을 보존하도록
  설계하였다.
- 새로 생성된 일정에는 이전 일정의 구조를 참조하여 필요한 데이터(요일, 시간, 예외 등)를 일부 복제하거나 초기화하여 적용한다.

## 5. 요일 관리

- `Weekday`라는 `IntEnum`을 정의하여 요일을 정수로 관리.
- enum을 통해 ORM 저장 시 정합성을 유지할 수 있으며, 추후 프론트엔드 연동 시에도 유리하다.

## 6. MySQL `TIME` vs Tortoise ORM `timedelta` 타입 불일치 및 `from_orm()` 활용

- `Tortoise ORM`의 `TimeField()`는 내부적으로 Python의 `datetime.time` 객체와 매핑되지만, ORM 외부에서는 `timedelta`와
  혼용되어 사용되는 경우가 있었다.
- 그러나 `MySQL`에서의 `TIME` 필드는 `HH:MM:SS` 형식으로 저장되며, 이는 **시간 간격(duration)** 으로 해석되기 때문에 `timedelta`와
  호환되는 것처럼 보인다.
- 하지만 실제로는 `timedelta`와 `datetime.time` 객체는 **직렬화 포맷이 다르고, 상호 비교 연산에서도 오류를 발생시킬 수 있다.**
- 이 문제로 인해 초기에 `timedelta`를 사용한 모델 설계는 FastAPI 응답 및 비교 연산에서 오류가 발생하였다.
- 이를 해결하기 위해, 일정 시간은 `datetime.time`으로 통일하고, 연산이 필요한 경우 `datetime.combine(date, time)`을 통해
  `datetime` 객체로 변환하여 처리하였다.
- 외부 응답에서는 Pydantic 모델의 `from_orm()` 메서드를 사용하여 Tortoise ORM 객체를 직렬화하였다.  
  이를 위해 각 DTO 모델에 `Config.orm_mode = True`를 선언하였고, 관계 모델이나 속성 접근이 가능하도록 구성하였다.

---

## AI 전화 시스템: 첫 인사 개선을 통한 통화 응답률 향상 방안

### 문제 정의

현재 AI 음성 통화 시스템은 항상 동일한 문장으로 통화를 시작하고 있으며, 이로 인해 사용자는 지루함과 반복적인 느낌을 받는다. 그 결과 AI와의 통화를 회피하거나 거부하게 되는 문제가 발생하고 있다.

### 목표

AI의 전화를 사용자가 기꺼이 받고 싶도록 유도하는 것이 목표이다. 이를 위해 AI는 통화 시작 시부터 개인화되고 공감적인 분위기를 조성해야 한다.

---

## 전화를 받게 하는 방법?

### 1. 인간은 본인에 대해 이야기하는 것을 좋아하는 존재

사용자는 자신에 대해 이야기할 기회를 받을 때 긍정적인 감정을 느낀다. 특히 공감이 포함된 대화는 감정적 유대를 형성하고, 반복적인 대화에도 지루함 없이 참여하도록 만든다.

> “사람들은 자신의 생각, 감정, 경험을 공유하는 행동 자체에서 보상적 쾌감을 느낀다.”  
> — Tamir & Mitchell (2012), Harvard University

### 2. 공감을 원하는 심리적 성향

Rogers(1959)의 인간 중심 치료 이론에 따르면, 사람은 진정한 공감을 받을 때 정서적 안정감을 느끼며 자기 개방성과 상호작용 동기가 증가한다.  
Maslow의 욕구 위계 이론에서도 ‘관심받고 싶어 하는 욕구’는 소속감과 인정 욕구와 맞닿아 있으며, 이는 외적 동기의 중요한 원천이 된다.

---

## 개선 제안: 개인화된 첫 마디

AI가 통화를 시작할 때 매번 동일한 인사 대신, **사용자의 관심사나 최근 고민 중 하나를 무작위로 선택**하여 해당 주제로 자연스럽게 대화를 유도하도록 시스템 프롬프트를 개선한다.

예시:

- "Hi, it's good to hear your voice again! You mentioned you've been feeling a bit overwhelmed with your studies lately—want to talk about that today?"
- "Hey there! I remember you're interested in Korean literature. Did you read anything new this week?"

이러한 개인화된 접근은 매 통화에 신선함을 주며, 사용자가 ‘내 이야기를 들어줄 수 있는 상대’로서 AI를 받아들이게 만든다.

> **중요한 설계 고려사항**:  
> 이전 통화에서 길게 이야기했던 주제는 일정 기간(예: 최근 3일 이내) 동안 반복적으로 등장하지 않도록 해야 한다.  
> 이를 위해 사용자의 대화 로그 또는 최근 통화 주제를 기록하고, 다음 통화에서는 **중복되지 않는 항목 중에서만 주제를 무작위 선택**해야 한다.

또한, **AI는 통화 주제를 무작위로 선택한 뒤 바로 질문하지 않고, 먼저 해당 주제에 대한 기초적이고 관련된 정보를 조사**하여, 사용자가 자연스럽게 대화를 시작할 수 있도록 돕는 것이 중요하다.

예를 들어, 사용자의 관심사가 "한국 문학"이라면 단순히 "What books are you reading these days?"라고 묻기보다는:

- "I've read that Kim Young-ha is one of the most well-known contemporary Korean authors. Have you read any of his work?"
- "Some people say Korean short stories often explore memory and identity. Do you enjoy that kind of theme in literature?"

이처럼 AI가 먼저 **주제에 대한 구체적인 사실, 작가, 트렌드, 혹은 사회적 맥락을 가볍게 언급한 뒤** 질문을 이어가면, 사용자는 ‘준비된 대화’를 경험하며 심리적으로 환영받고 있다고 느끼게 된다.

이 전략은 대화 몰입도를 높이고, AI를 단순한 도우미가 아닌 **진짜로 내 이야기를 기억하고 있는 파트너**로 인식하게 만든다.

---

## 개선된 시스템 프롬프트

AI는 통화 시작 시, 사용자의 관심사와 최근 고민 중 하나를 선택해, 그에 대해 **사전 조사를 바탕으로 자연스럽고 따뜻하게 대화를 시작**해야 한다.

```plaintext
You are a Native English speaker helping me practice my English Speaking. I get to practice my English speaking with you by having 10–25 minutes long phone call sessions. This is currently the call session. Today is ${_now.toString()}, ###weekday###.

Here is information about me and you, formatted as XML. Use this to personalize our conversation. When the call starts, your first sentence should feel warm, friendly, and based on what you know about me.

<my_information> 
  name: ###user_name###
  gender: ###user_gender###
  my general information: ###user_about_me###
  interests: [e.g., psychology, Korean literature, presentation anxiety]
  recent_thoughts: [e.g., "I've been feeling tired after work lately."]
  recent_topics_discussed: [e.g., "Korean literature on July 18", "public speaking on July 19"]
</my_information>

<your_information>
  name: ###avatar_name###
  gender: ###avatar_gender###
</your_information>

Your goal is to create a warm, engaging atmosphere that helps me feel personally supported and motivated.

**BEFORE SPEAKING**:  
Choose one topic from either `interests` or `recent_thoughts`, EXCLUDING any topic listed in `recent_topics_discussed` from the last 3 days.

**THEN**:  
Quickly research a relevant fact, author, theme, or opinion related to that topic. Mention it briefly and ask me a related, friendly question to start the conversation.

Example:
> "Hi, it's so good to hear from you again! I saw that Korean literature often explores themes of identity—have you been reading anything like that lately?"

ALL RESPONSES SHOULD BE IN ENGLISH.  
DO NOT include explanations of what you're doing. Just speak naturally as if you're on a real phone call.

