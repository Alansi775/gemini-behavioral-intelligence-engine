import fs from "fs";

/**
 * Generate realistic human daily activity logs
 * Multiple roles, timestamps, actions, outcomes, mistakes
 */

const ROLES = {
  developer: "software_developer",
  office: "office_employee",
  student: "student",
  driver: "driver"
};

// ============================================================================
// ROLE 1: SOFTWARE DEVELOPER
// ============================================================================
function generateDeveloperLogs() {
  const events = [];
  const logFile = "logs/developer_daily.jsonl";

  events.push(
    { time: "08:30", action: "arrives_office", detail: "opens laptop", outcome: "ready_to_work" },
    { time: "08:32", action: "checks_email", detail: "3 messages from team", outcome: "sees_urgent_flag", error: "context_switch" },
    { time: "08:35", action: "checks_slack", detail: "2 pending messages", outcome: "acknowledges_but_not_reading", error: "shallow_processing" },
    { time: "08:38", action: "opens_pull_request", detail: "12 files changed, feature branch", outcome: "reviews_code", error: "skips_local_test" },
    { time: "08:42", action: "approves_pr", detail: "no test output attached", outcome: "pr_merged", error: "false_verification" },
    { time: "08:43", action: "deploys_to_staging", detail: "merged code deployed", outcome: "deployment_complete", error: "no_smoke_test" },
    { time: "08:50", action: "slack_message_received", detail: "QA asks did you test?", outcome: "replies_yes", error: "dishonest_status" },
    { time: "09:00", action: "standup_meeting", detail: "reports PR complete and tested", outcome: "team_marks_ready", error: "false_claim_escalated" },
    { time: "09:35", action: "email_from_qa", detail: "staging crashed during test", outcome: "realizes_error", error: "late_detection" },
    { time: "09:38", action: "checks_logs", detail: "nullpointerexception in payment module", outcome: "identifies_bug_source", error: "cascade_failure" },
    { time: "09:42", action: "attempts_rollback", detail: "tries to revert PR on staging", outcome: "rollback_partial_success", error: "data_corruption" },
    { time: "09:48", action: "notifies_manager", detail: "production affected", outcome: "emergency_meeting", error: "team_overhead" },
    { time: "09:55", action: "creates_hotfix", detail: "fixes uninitialized variable", outcome: "hotfix_branch_ready", error: "no_peer_review" },
    { time: "10:05", action: "deploys_hotfix", detail: "goes directly to production", outcome: "system_online", error: "skipped_staging_retest" },
    { time: "10:20", action: "posts_incident_report", detail: "minimal info: null pointer bug", outcome: "status_shared", error: "no_root_cause_analysis" },
    { time: "10:35", action: "returns_to_work", detail: "opens next PR for review", outcome: "resumes_normal_tasks", error: "pattern_repeats" },
    { time: "11:10", action: "next_pr_reviewed", detail: "skims changes again", outcome: "approves_without_testing", error: "same_pattern_repeats" },
    { time: "12:00", action: "lunch_break", detail: "leaves desk", outcome: "no_documentation", error: "learning_opportunity_lost" }
  );

  const jsonl = events.map(e => JSON.stringify(e)).join('\n');
  if (!fs.existsSync('logs')) fs.mkdirSync('logs');
  fs.writeFileSync(logFile, jsonl);
  console.log(`✓ Generated ${events.length} developer events`);
  return events;
}

// ============================================================================
// ROLE 2: OFFICE EMPLOYEE
// ============================================================================
function generateOfficeLogs() {
  const events = [];
  const logFile = "logs/office_employee_daily.jsonl";

  events.push(
    { time: "08:45", action: "arrives_office", detail: "coffee, checks emails", outcome: "seated_at_desk" },
    { time: "08:55", action: "reads_emails", detail: "12 emails, 3 marked urgent", outcome: "replies_to_some", error: "skips_reading_full_context" },
    { time: "09:10", action: "starts_task_1", detail: "project report due today", outcome: "opens_document", error: "interruption_incoming" },
    { time: "09:15", action: "colleague_interruption", detail: "asks quick question", outcome: "answers", error: "loses_focus" },
    { time: "09:20", action: "returns_to_task_1", detail: "tries to continue report", outcome: "restarts_train_of_thought", error: "time_lost" },
    { time: "09:45", action: "receives_email", detail: "manager: need report NOW", outcome: "increases_urgency", error: "rush_begins" },
    { time: "09:50", action: "rushes_report", detail: "skips proofreading", outcome: "sends_report", error: "unreviewed_typos" },
    { time: "10:15", action: "receives_reply", detail: "manager: found 3 typos, unprofessional", outcome: "embarrassed", error: "quality_issue" },
    { time: "10:30", action: "fixes_typos", detail: "sends_corrected_version", outcome: "manager_OK", error: "reputation_damage" },
    { time: "11:00", action: "team_meeting", detail: "sitting in meeting", outcome: "checks_phone", error: "not_paying_attention" },
    { time: "11:45", action: "asks_clarifying_question", detail: "something discussed 20 minutes ago", outcome: "everyone_silent", error: "distraction_caught" },
    { time: "12:00", action: "lunch_meeting", detail: "business lunch scheduled", outcome: "eats_while_talking", error: "multitasking" },
    { time: "13:15", action: "afternoon_tasks", detail: "starts new project task", outcome: "working", error: "another_interruption" },
    { time: "13:25", action: "colleague_asks_favor", detail: "can you do this small thing?", outcome: "says_yes", error: "task_context_switch" },
    { time: "14:00", action: "realizes_due_date", detail: "original_task_due_tomorrow", outcome: "stress_increases", error: "timeline_pressure" },
    { time: "14:30", action: "multitasks_two_tasks", detail: "switches between both", outcome: "completes_neither_well", error: "split_attention" },
    { time: "15:45", action: "emergency_request", detail: "manager needs analysis", outcome: "prioritizes_over_scheduled_tasks", error: "task_queue_chaos" },
    { time: "17:00", action: "end_of_day", detail: "leaves incomplete tasks", outcome: "tomorrow_will_be_worse", error: "technical_debt_accumulates" }
  );

  const jsonl = events.map(e => JSON.stringify(e)).join('\n');
  fs.writeFileSync(logFile, jsonl);
  console.log(`✓ Generated ${events.length} office employee events`);
  return events;
}

// ============================================================================
// ROLE 3: STUDENT
// ============================================================================
function generateStudentLogs() {
  const events = [];
  const logFile = "logs/student_daily.jsonl";

  events.push(
    { time: "07:30", action: "alarm_goes_off", detail: "5:30 AM", outcome: "hits_snooze", error: "procrastination_begins" },
    { time: "07:45", action: "alarm_again", detail: "4th snooze", outcome: "finally_gets_up", error: "late_rush" },
    { time: "08:00", action: "breakfast", detail: "skipped", outcome: "rushed_to_school", error: "no_fuel" },
    { time: "08:25", action: "arrives_school", detail: "running", outcome: "barely_on_time", error: "stressed_start" },
    { time: "08:30", action: "first_class", detail: "math", outcome: "sits_in_back", error: "poor_visibility" },
    { time: "08:35", action: "takes_notes", detail: "writes randomly", outcome: "messy_notes", error: "poor_documentation" },
    { time: "09:15", action: "text_from_friend", detail: "asks to copy homework", outcome: "shares_homework", error: "academic_dishonesty" },
    { time: "09:45", action: "second_class", detail: "english", outcome: "sits_with_friends", error: "distraction" },
    { time: "10:00", action: "talks_during_class", detail: "getting_louder", outcome: "teacher_warns", error: "ignored_warning" },
    { time: "10:15", action: "teacher_assigns_homework", detail: "essay due tomorrow", outcome: "thinks_will_do_tonight", error: "false_plan" },
    { time: "12:00", action: "lunch", detail: "spends_all_break_socializing", outcome: "no_homework_progress", error: "time_misallocation" },
    { time: "13:00", action: "afternoon_classes", detail: "3 more classes", outcome: "takes_more_notes", error: "still_messy" },
    { time: "15:30", action: "school_ends", detail: "goes_home", outcome: "thinks_will_do_homework", error: "unrealistic_plan" },
    { time: "16:00", action: "arrives_home", detail: "video_games_friends_online", outcome: "plays_games", error: "procrastination" },
    { time: "18:00", action: "dinner_time", detail: "stops_for_dinner", outcome: "eats_while_gaming", error: "distracted_eating" },
    { time: "19:00", action: "realizes_essay_due", detail: "suddenly_remembers", outcome: "panics", error: "late_realization" },
    { time: "19:15", action: "starts_essay", detail: "1 hour left till_deadline", outcome: "rushes_writing", error: "quality_suffers" },
    { time: "20:00", action: "submits_essay", detail: "incomplete, full_of_errors", outcome: "submitted_last_minute", error: "poor_grade_expected" },
    { time: "20:30", action: "realizes_missed_study", detail: "test_tomorrow_in_math", outcome: "panic", error: "unprepared" }
  );

  const jsonl = events.map(e => JSON.stringify(e)).join('\n');
  fs.writeFileSync(logFile, jsonl);
  console.log(`✓ Generated ${events.length} student events`);
  return events;
}

// ============================================================================
// ROLE 4: DRIVER
// ============================================================================
function generateDriverLogs() {
  const events = [];
  const logFile = "logs/driver_daily.jsonl";

  events.push(
    { time: "07:30", action: "wakes_up", detail: "alarm", outcome: "groggy", error: "not_fully_alert" },
    { time: "07:50", action: "checks_weather", detail: "rainy", outcome: "decides_to_drive", error: "no_extra_time_planned" },
    { time: "08:00", action: "gets_in_car", detail: "cold_engine", outcome: "starts_driving", error: "no_warm_up" },
    { time: "08:05", action: "traffic_jam_ahead", detail: "unexpected_congestion", outcome: "stressed", error: "no_buffer_time" },
    { time: "08:15", action: "checks_phone", detail: "looking_at_map", outcome: "eyes_off_road", error: "distracted_driving" },
    { time: "08:20", action: "almost_misses_turn", detail: "last_second_maneuver", outcome: "honks_from_other_car", error: "reckless_maneuver" },
    { time: "08:30", action: "receives_call", detail: "boss_calling", outcome: "answers_phone", error: "driving_with_one_hand" },
    { time: "08:45", action: "arrives_work_late", detail: "traffic_made_late", outcome: "rushed_to_office", error: "stress" },
    { time: "17:30", action: "leaves_work", detail: "tired", outcome: "gets_in_car", error: "fatigue" },
    { time: "17:35", action: "stop_sign", detail: "stops", outcome: "looks_at_text_message", error: "eyes_off_road" },
    { time: "17:40", action: "light_turns_green", detail: "someone_honks", outcome: "looks_up_startled", error: "reaction_delayed" },
    { time: "18:00", action: "highway_driving", detail: "monotonous_road", outcome: "thinking_about_work", error: "mind_not_focused" },
    { time: "18:15", action: "feels_drowsy", detail: "eyelids_heavy", outcome: "tries_to_stay_awake", error: "fighting_fatigue" },
    { time: "18:30", action: "music_too_loud", detail: "loud_music_playing", outcome: "can't_hear_sirens", error: "poor_situational_awareness" },
    { time: "18:45", action: "sudden_brake", detail: "car_ahead_brakes_suddenly", outcome: "barely_stops", error: "following_too_close" },
    { time: "19:00", action: "arrives_home", detail: "safe_but_stressed", outcome: "exhausted", error: "accumulated_stress" },
    { time: "19:30", action: "plans_tomorrow_commute", detail: "thinks_will_wake_earlier", outcome: "same_plan_as_today", error: "no_actual_change" }
  );

  const jsonl = events.map(e => JSON.stringify(e)).join('\n');
  fs.writeFileSync(logFile, jsonl);
  console.log(`✓ Generated ${events.length} driver events`);
  return events;
}

// ============================================================================
// Main execution
// ============================================================================
console.log(" Generating Human Daily Activity Logs\n");

generateDeveloperLogs();
generateOfficeLogs();
generateStudentLogs();
generateDriverLogs();

console.log("\n All logs generated successfully!");
console.log("Files created:");
console.log("  - logs/developer_daily.jsonl");
console.log("  - logs/office_employee_daily.jsonl");
console.log("  - logs/student_daily.jsonl");
console.log("  - logs/driver_daily.jsonl");
