import time

from datetime import datetime, timezone

from agent.investigator import get_current_health
from agent.agent import investigate_incident
from agent.correlation import correlate_signals

from agent.incident_store import (
    create_incident,
    update_incident,
    mark_investigation_complete,
    mark_recovered,
)

from tools.slack import send_slack_message

from tools.jira import (
    create_incident_issue,
    add_comment,
    move_issue_to_in_progress,
    move_issue_to_done,
)


# ============================================================
# CONFIGURATION
# ============================================================

CHECK_INTERVAL = 30

RECOVERY_CHECKS_REQUIRED = 3

INCIDENT_PERSISTENCE_ENABLED = True


# ============================================================
# INCIDENT STATE
# ============================================================

incident_active = False

incident_id = None

incident_detected_at = None

healthy_checks = 0

jira_issue_key = None


# ============================================================
# SLACK NOTIFICATION
# ============================================================

def notify_slack(message):
    try:
        send_slack_message(message)

        print(
            "📨 Slack notification sent."
        )

    except Exception as exc:
        print(
            f"⚠️ Slack notification failed: {exc}"
        )


# ============================================================
# CORRELATION DISPLAY
# ============================================================

def display_correlation(correlation):
    print("\n")
    print("=" * 60)
    print("        ALERT CORRELATION")
    print("=" * 60)

    print(
        f"Correlated: "
        f"{correlation.get('correlated')}"
    )

    print(
        f"Signal Count: "
        f"{correlation.get('signal_count')}"
    )

    print(
        f"Correlation Severity: "
        f"{correlation.get('severity')}"
    )

    print(
        f"Summary: "
        f"{correlation.get('summary')}"
    )

    signals = correlation.get(
        "signals",
        []
    )

    if signals:
        print("\nSignals:")

        for index, signal in enumerate(
            signals,
            start=1
        ):
            print(
                f"{index}. "
                f"{signal.get('type')} | "
                f"{signal.get('severity')} | "
                f"{signal.get('message')}"
            )

    else:
        print("\nSignals:")
        print("No active signals.")

    print("=" * 60)


def build_correlation_text(correlation):
    signals = correlation.get(
        "signals",
        []
    )

    if not signals:
        return (
            "No active correlated signals."
        )

    lines = []

    for index, signal in enumerate(
        signals,
        start=1
    ):
        lines.append(
            f"{index}. "
            f"{signal.get('type')} | "
            f"Severity: {signal.get('severity')} | "
            f"Message: {signal.get('message')}"
        )

    return "\n".join(lines)


# ============================================================
# JIRA INCIDENT CREATION
# ============================================================

def notify_jira_incident(
    incident_id,
    severity,
    detected_at,
    health,
    investigation,
    correlation
):
    try:

        issue = create_incident_issue(
            incident_id=incident_id,
            severity=severity,
            detected_at=detected_at,
            cpu=health["cpu"],
            memory=health["memory"],
            incident_mode=health["incident_mode"],
            investigation=investigation,
        )

        issue_key = issue.get(
            "key"
        )

        print(
            f"🎫 Jira incident created: "
            f"{issue_key}"
        )

        if issue_key:

            print(
                "Jira URL: "
                f"https://tushardevops.atlassian.net/"
                f"browse/{issue_key}"
            )

            # ------------------------------------------------
            # MOVE JIRA ISSUE TO IN PROGRESS
            # ------------------------------------------------

            try:

                move_issue_to_in_progress(
                    issue_key
                )

                print(
                    f"🔄 Jira issue {issue_key} "
                    "moved to IN PROGRESS."
                )

            except Exception as exc:

                print(
                    "⚠️ Failed to move Jira issue "
                    f"{issue_key} to IN PROGRESS: {exc}"
                )

            # ------------------------------------------------
            # Add correlation evidence to Jira
            # ------------------------------------------------

            correlation_comment = (
                "AI NOC Alert Correlation\n\n"
                f"Correlated: "
                f"{correlation.get('correlated')}\n"
                f"Signal Count: "
                f"{correlation.get('signal_count')}\n"
                f"Correlation Severity: "
                f"{correlation.get('severity')}\n\n"
                "Correlation Summary:\n"
                f"{correlation.get('summary')}\n\n"
                "Detected Signals:\n"
                f"{build_correlation_text(correlation)}"
            )

            try:

                add_comment(
                    issue_key=issue_key,
                    comment=correlation_comment
                )

                print(
                    "🔗 Jira correlation evidence added."
                )

            except Exception as exc:

                print(
                    "⚠️ Failed to add Jira "
                    f"correlation comment: {exc}"
                )

        return issue_key

    except Exception as exc:

        print(
            "⚠️ Jira incident creation failed: "
            f"{exc}"
        )

        return None


# ============================================================
# JIRA RECOVERY UPDATE
# ============================================================

def notify_jira_recovery(
    issue_key,
    incident_id,
    healthy_checks,
    health
):

    if not issue_key:

        print(
            "⚠️ No Jira issue key available "
            "for recovery update."
        )

        return

    try:

        recovery_comment = (
            "AI NOC Incident Recovered\n\n"
            f"Incident ID: {incident_id}\n"
            f"Recovery confirmed after "
            f"{healthy_checks} consecutive "
            "healthy checks.\n\n"
            f"Current CPU: {health['cpu']}%\n"
            f"Current Memory: {health['memory']}%\n"
            f"Current Incident Mode: "
            f"{health['incident_mode']}\n\n"
            "The incident condition has cleared "
            "and recovery has been confirmed "
            "by the AI NOC monitoring detector."
        )

        add_comment(
            issue_key=issue_key,
            comment=recovery_comment
        )

        print(
            f"🔄 Jira recovery update added "
            f"to {issue_key}."
        )

        # ------------------------------------------------
        # MOVE JIRA ISSUE TO DONE
        # ------------------------------------------------

        try:

            move_issue_to_done(
                issue_key
            )

            print(
                f"✅ Jira issue {issue_key} "
                "moved to DONE."
            )

        except Exception as exc:

            print(
                "⚠️ Failed to move Jira issue "
                f"{issue_key} to DONE: {exc}"
            )

    except Exception as exc:

        print(
            "⚠️ Jira recovery update failed: "
            f"{exc}"
        )


# ============================================================
# INCIDENT ID
# ============================================================

def generate_incident_id():

    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    return f"INC-{timestamp}"


# ============================================================
# DISPLAY HEALTH
# ============================================================

def display_health(health):

    print("\n" + "-" * 50)

    print(
        "Checking system health..."
    )

    print(
        f"CPU: {health['cpu']}%"
    )

    print(
        f"Memory: {health['memory']}%"
    )

    print(
        f"Severity: {health['severity']}"
    )

    print(
        f"Incident Mode: "
        f"{health['incident_mode']}"
    )

    print(
        f"Error Percentage: "
        f"{health['error_percentage']}"
    )


# ============================================================
# INCIDENT DETECTION RULE
# ============================================================

def is_incident(
    health,
    correlation
):

    # Existing direct incident trigger
    if health["incident_mode"] == 1:
        return True

    # Existing critical health trigger
    if health["severity"] == "CRITICAL":
        return True

    # Correlation is used as supporting evidence.
    # A HIGH correlated event alone does not create
    # an incident automatically.

    return False


# ============================================================
# START INCIDENT
# ============================================================

def start_incident(
    health,
    correlation
):

    global incident_active
    global incident_id
    global incident_detected_at
    global healthy_checks
    global jira_issue_key

    incident_active = True

    healthy_checks = 0

    jira_issue_key = None

    # --------------------------------------------------------
    # Generate Incident ID
    # --------------------------------------------------------

    incident_id = generate_incident_id()

    # --------------------------------------------------------
    # Detection timestamp
    # --------------------------------------------------------

    incident_detected_at = datetime.now(
        timezone.utc
    ).isoformat()

    print("\n")

    print("=" * 60)

    print(
        "🚨 INCIDENT DETECTED"
    )

    print("=" * 60)

    print(
        f"Incident ID: "
        f"{incident_id}"
    )

    print(
        f"Detected At: "
        f"{incident_detected_at}"
    )

    print("\nIncident Evidence:")

    print(
        f"CPU: "
        f"{health['cpu']}%"
    )

    print(
        f"Memory: "
        f"{health['memory']}%"
    )

    print(
        f"Incident Mode: "
        f"{health['incident_mode']}"
    )

    print(
        f"Severity: "
        f"{health['severity']}"
    )

    # --------------------------------------------------------
    # Correlation evidence
    # --------------------------------------------------------

    print(
        "\n🔗 Correlated Incident Evidence"
    )

    display_correlation(
        correlation
    )

    # ========================================================
    # CREATE INCIDENT STORE RECORD
    # ========================================================

    print(
        "\n💾 Creating incident record..."
    )

    try:

        create_incident(
            incident_id=incident_id,
            severity=health["severity"],
            cpu=health["cpu"],
            memory=health["memory"],
            incident_mode=health["incident_mode"],
        )

        update_incident(
            incident_id,
            detected_at=incident_detected_at,
            updated_at=incident_detected_at,
            correlation=correlation,
        )

        print(
            "💾 Incident stored successfully."
        )

    except Exception as exc:

        print(
            "⚠️ Incident store creation "
            f"failed: {exc}"
        )

    # ========================================================
    # SLACK INCIDENT MESSAGE
    # ========================================================

    correlation_text = (
        build_correlation_text(
            correlation
        )
    )

    slack_incident_message = f"""
🚨 *AI NOC Incident Detected*

*Incident ID:* {incident_id}

*Detected At:* {incident_detected_at}

*Severity:* {health['severity']}

*Current Evidence*
• CPU: {health['cpu']}%
• Memory: {health['memory']}%
• Incident Mode: {health['incident_mode']}
• Error Percentage: {health['error_percentage']}

🔗 *Alert Correlation*
• Correlated: {correlation.get('correlated')}
• Signal Count: {correlation.get('signal_count')}
• Correlation Severity: {correlation.get('severity')}

*Correlation Summary*
{correlation.get('summary')}

*Detected Signals*
{correlation_text}

💾 Incident has been stored locally.

🤖 AI investigation is in progress.
"""

    notify_slack(
        slack_incident_message
    )

    # ========================================================
    # AI INVESTIGATION
    # ========================================================

    print(
        "\nCollecting evidence..."
    )

    print(
        "Sending incident evidence "
        "to local AI..."
    )

    try:

        analysis = investigate_incident(
            return_analysis=True,
            incident_id=incident_id,
            detected_at=incident_detected_at
        )

        print("\n")

        print("=" * 60)

        print(
            "🤖 AI INVESTIGATION COMPLETED"
        )

        print("=" * 60)

        print(
            f"Incident ID: "
            f"{incident_id}"
        )

        print(
            f"Detected At: "
            f"{incident_detected_at}"
        )

        print(
            "\n" + analysis
        )

        print("=" * 60)

        # ====================================================
        # SAVE AI INVESTIGATION
        # ====================================================

        print(
            "\n💾 Saving AI investigation..."
        )

        try:

            mark_investigation_complete(
                incident_id=incident_id,
                analysis=analysis
            )

            print(
                "💾 AI investigation "
                "saved successfully."
            )

        except Exception as exc:

            print(
                "⚠️ Failed to save AI "
                f"investigation: {exc}"
            )

        # ====================================================
        # SLACK AI REPORT
        # ====================================================

        slack_ai_message = f"""
🤖 *AI NOC Investigation Completed*

*Incident ID:* {incident_id}

*Detected At:* {incident_detected_at}

*AI Investigation Report*

{analysis}

🔗 *Correlated Signals*

{correlation_text}
"""

        notify_slack(
            slack_ai_message
        )

        # ====================================================
        # CREATE JIRA ISSUE
        # ====================================================

        jira_issue_key = notify_jira_incident(

            incident_id=incident_id,

            severity=health["severity"],

            detected_at=incident_detected_at,

            health=health,

            investigation=analysis,

            correlation=correlation
        )

        # ====================================================
        # SAVE JIRA ISSUE KEY
        # ====================================================

        if jira_issue_key:

            try:

                update_incident(
                    incident_id,
                    jira_issue_key=jira_issue_key
                )

                print(
                    "💾 Jira issue key "
                    "saved to incident store."
                )

            except Exception as exc:

                print(
                    "⚠️ Failed to save Jira "
                    f"issue key: {exc}"
                )

    except Exception as exc:

        print(
            "\n❌ AI investigation failed."
        )

        print(
            f"Error: {exc}"
        )

        print(
            "\nThe monitoring detector "
            "will continue running."
        )

        # ====================================================
        # SAVE AI FAILURE
        # ====================================================

        try:

            mark_investigation_complete(
                incident_id=incident_id,
                analysis=(
                    "AI investigation failed.\n\n"
                    f"Error: {exc}"
                )
            )

        except Exception as store_exc:

            print(
                "⚠️ Failed to save AI "
                f"failure state: {store_exc}"
            )

        # ====================================================
        # SLACK AI FAILURE
        # ====================================================

        slack_ai_failure_message = f"""
⚠️ *AI NOC Investigation Failed*

*Incident ID:* {incident_id}

The incident was detected successfully,
but the AI investigation could not be completed.

*Error:*
{exc}

*Correlated Signals*

{correlation_text}

The NOC detector is continuing to monitor the system.
"""

        notify_slack(
            slack_ai_failure_message
        )

        # ====================================================
        # JIRA ISSUE EVEN IF AI FAILS
        # ====================================================

        jira_issue_key = notify_jira_incident(

            incident_id=incident_id,

            severity=health["severity"],

            detected_at=incident_detected_at,

            health=health,

            investigation=(
                "AI investigation failed.\n\n"
                f"Error: {exc}"
            ),

            correlation=correlation
        )

        if jira_issue_key:

            try:

                update_incident(
                    incident_id,
                    jira_issue_key=jira_issue_key
                )

            except Exception as store_exc:

                print(
                    "⚠️ Failed to save Jira "
                    f"issue key: {store_exc}"
                )


# ============================================================
# ACTIVE INCIDENT
# ============================================================

def handle_active_incident(
    health,
    correlation
):

    global healthy_checks

    healthy_checks = 0

    print(
        "\n⚠️ INCIDENT STILL ACTIVE"
    )

    print(
        f"Incident ID: "
        f"{incident_id}"
    )

    print(
        f"CPU: "
        f"{health['cpu']}%"
    )

    print(
        f"Memory: "
        f"{health['memory']}%"
    )

    print(
        f"Severity: "
        f"{health['severity']}"
    )

    print(
        f"Correlated Signals: "
        f"{correlation.get('signal_count')}"
    )

    print(
        "\nSkipping duplicate AI investigation."
    )

    print(
        "The existing incident remains active."
    )


# ============================================================
# RECOVERY
# ============================================================

def check_recovery(
    health,
    correlation
):

    global incident_active
    global incident_id
    global incident_detected_at
    global healthy_checks
    global jira_issue_key

    healthy_checks += 1

    print(
        "\n🔎 RECOVERY CHECK"
    )

    print(
        f"Healthy checks: "
        f"{healthy_checks}/"
        f"{RECOVERY_CHECKS_REQUIRED}"
    )

    # ========================================================
    # INCIDENT STILL NOT RECOVERED
    # ========================================================

    if healthy_checks < RECOVERY_CHECKS_REQUIRED:

        try:

            update_incident(

                incident_id,

                recovery={
                    "healthy_checks":
                        healthy_checks,

                    "required_checks":
                        RECOVERY_CHECKS_REQUIRED,

                    "recovered_at":
                        None
                }
            )

        except Exception as exc:

            print(
                "⚠️ Failed to update "
                f"recovery progress: {exc}"
            )

        return

    # ========================================================
    # INCIDENT RECOVERED
    # ========================================================

    print("\n")

    print("=" * 60)

    print(
        "✅ INCIDENT RECOVERED"
    )

    print("=" * 60)

    print(
        f"Incident ID: "
        f"{incident_id}"
    )

    print(
        f"Recovery confirmed after "
        f"{healthy_checks} consecutive "
        "healthy checks."
    )

    print(
        f"Current CPU: "
        f"{health['cpu']}%"
    )

    print(
        f"Current Memory: "
        f"{health['memory']}%"
    )

    print(
        f"Current Incident Mode: "
        f"{health['incident_mode']}"
    )

    print("=" * 60)

    # ========================================================
    # UPDATE INCIDENT STORE
    # ========================================================

    try:

        mark_recovered(

            incident_id=incident_id,

            cpu=health["cpu"],

            memory=health["memory"],

            incident_mode=health["incident_mode"]
        )

        print(
            "💾 Incident store updated: "
            "RECOVERED"
        )

    except Exception as exc:

        print(
            "⚠️ Failed to mark incident "
            f"recovered in store: {exc}"
        )

    # ========================================================
    # SLACK RECOVERY
    # ========================================================

    slack_recovery_message = f"""
✅ *AI NOC Incident Recovered*

*Incident ID:* {incident_id}

*Recovery confirmed after:* {healthy_checks} consecutive healthy checks

*Current CPU:* {health['cpu']}%
*Current Memory:* {health['memory']}%
*Incident Mode:* {health['incident_mode']}

The incident condition has cleared and recovery
has been confirmed.
"""

    notify_slack(
        slack_recovery_message
    )

    # ========================================================
    # JIRA RECOVERY
    # ========================================================

    notify_jira_recovery(

        issue_key=jira_issue_key,

        incident_id=incident_id,

        healthy_checks=healthy_checks,

        health=health
    )

    # ========================================================
    # RESET DETECTOR STATE
    # ========================================================

    incident_active = False

    incident_id = None

    incident_detected_at = None

    healthy_checks = 0

    jira_issue_key = None


# ============================================================
# MAIN DETECTOR
# ============================================================

def run_detector():

    global incident_active

    print("\n")

    print("=" * 60)

    print(
        "        AI NOC AUTOMATIC DETECTOR"
    )

    print("=" * 60)

    print(
        f"Check interval: "
        f"{CHECK_INTERVAL} seconds"
    )

    print(
        f"Recovery checks required: "
        f"{RECOVERY_CHECKS_REQUIRED}"
    )

    print(
        "Incident persistence: "
        f"{'ENABLED' if INCIDENT_PERSISTENCE_ENABLED else 'DISABLED'}"
    )

    print(
        "Slack integration: ENABLED"
    )

    print(
        "Jira integration: ENABLED"
    )

    print(
        "Incident Store: ENABLED"
    )

    print(
        "Alert Correlation: ENABLED"
    )

    print(
        "Detector started..."
    )

    print(
        "Press Ctrl+C to stop."
    )

    while True:

        try:

            # =================================================
            # COLLECT HEALTH
            # =================================================

            health = get_current_health()

            display_health(
                health
            )

            # =================================================
            # CORRELATE ALERT SIGNALS
            # =================================================

            correlation = correlate_signals(
                health
            )

            display_correlation(
                correlation
            )

            # =================================================
            # INCIDENT DETECTION
            # =================================================

            current_incident = is_incident(
                health,
                correlation
            )

            # =================================================
            # NEW INCIDENT
            # =================================================

            if (
                current_incident
                and not incident_active
            ):

                start_incident(
                    health,
                    correlation
                )

            # =================================================
            # INCIDENT STILL ACTIVE
            # =================================================

            elif (
                current_incident
                and incident_active
            ):

                handle_active_incident(
                    health,
                    correlation
                )

            # =================================================
            # RECOVERY
            # =================================================

            elif (
                not current_incident
                and incident_active
            ):

                if INCIDENT_PERSISTENCE_ENABLED:

                    check_recovery(
                        health,
                        correlation
                    )

                else:

                    print(
                        "\n✅ Incident condition cleared."
                    )

                    incident_active = False

            # =================================================
            # HEALTHY / ATTENTION STATE
            # =================================================

            else:

                signal_count = correlation.get(
                    "signal_count",
                    0
                )

                if signal_count > 0:

                    print(
                        "\n⚠️ SYSTEM REQUIRES ATTENTION"
                    )

                    print(
                        "Active correlation signals: "
                        f"{signal_count}"
                    )

                    print(
                        "Correlation severity: "
                        f"{correlation.get('severity')}"
                    )

                    print(
                        "No incident was opened because "
                        "the current incident policy requires "
                        "CRITICAL severity or incident mode."
                    )

                else:

                    print(
                        "\n✅ SYSTEM HEALTHY"
                    )

            print(
                f"\nNext check in "
                f"{CHECK_INTERVAL} seconds..."
            )

            time.sleep(
                CHECK_INTERVAL
            )

        except KeyboardInterrupt:

            print(
                "\n\n🛑 Detector stopped by user."
            )

            break

        except Exception as exc:

            print(
                "\n❌ Detector error."
            )

            print(
                f"Error: {exc}"
            )

            print(
                "\nThe detector will continue running."
            )

            print(
                f"Next check in "
                f"{CHECK_INTERVAL} seconds..."
            )

            time.sleep(
                CHECK_INTERVAL
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_detector()