import os
import sys
from absl import app, flags
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from multi_tool_agent.agent import root_agent
from vertexai import agent_engines
import vertexai

FLAGS = flags.FLAGS
flags.DEFINE_bool("create", False, "Creates a new deployment.")
flags.DEFINE_bool("delete", False, "Deletes an existing deployment.")
flags.DEFINE_bool("quicktest", False, "Runs a quick test with the deployed agent.")
flags.DEFINE_string("project_id", None, "Google Cloud project ID.")
flags.DEFINE_string("location", None, "Google Cloud location.")
flags.DEFINE_string("bucket", None, "Google Cloud Storage bucket.")
flags.DEFINE_string("resource_id", None, "Resource ID for operations.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete", "quicktest"])


def create(env_vars: dict[str, str]) -> None:
    """Creates a new deployment."""
    print(env_vars)
    remote_app = agent_engines.create(
        agent_engine=root_agent,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]"   
        ]
    )
    print(f"Created remote agent: {remote_app.resource_name}")


def delete(resource_id: str) -> None:
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"Deleted remote agent: {resource_id}")


def send_message(resource_id: str, message: str) -> None:
    """Send a message to the deployed agent."""
    try:
        remote_agent = agent_engines.get(resource_id)
        print(f"Successfully connected to remote agent: {resource_id}")
        
        # Try to send message without session first
        try:
            print(f"Sending message to remote agent: {resource_id}")
            for event in remote_agent.stream_query(
                user_id="traveler0115",
                message=message,
            ):
                print(event)
            print("Done.")
            return
            
        except Exception as stream_error:
            print(f"Stream query without session failed: {stream_error}")
            
            # Try creating session first
            try:
                print("Attempting to create session...")
                session = remote_agent.create_session(
                    user_id="traveler0115"
                )
                print(f"Session created successfully: {session['id']}")
                
                print(f"Trying remote agent with session: {resource_id}")
                for event in remote_agent.stream_query(
                    user_id="traveler0115",
                    session_id=session["id"],
                    message=message,
                ):
                    print(event)
                print("Done.")
                
            except Exception as session_error:
                print(f"Session-based query also failed: {session_error}")
                print("This indicates a fundamental issue with the deployed agent.")
                print("Consider redeploying the agent or checking the agent implementation.")
                return
        
    except Exception as e:
        print(f"Error connecting to remote agent {resource_id}: {e}")
        print("Please check if the agent is deployed correctly.")
        return


def main(argv: list[str]) -> None:

    # Load environment variables from the multi_tool_agent directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'multi_tool_agent', '.env')
    load_dotenv(env_path)
    env_vars = {}

    project_id = (
        FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET")
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.create:
        create(env_vars)
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    elif FLAGS.quicktest:
        if not FLAGS.resource_id:
            print("resource_id is required for quicktest")
            return
        send_message(FLAGS.resource_id, "Looking for inspirations around the Americas")
    else:
        print("Unknown command")


if __name__ == "__main__":
    app.run(main)
