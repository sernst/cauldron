import os
import shutil

MY_DIRECTORY = os.path.realpath(os.path.dirname(__file__))


def main():
    """Copies the current dist directory into the cauldron Python package."""
    print('\n\n=== DEPLOYING ====\n')
    dist_path = os.path.join(MY_DIRECTORY, 'dist')
    deploy_path = os.path.realpath(os.path.join(
        MY_DIRECTORY,
        '..', 'cauldron', 'resources', 'web'
    ))
    print(f'DIST PATH: {dist_path}')
    print(f'DEPLOY PATH: {deploy_path}')

    print(f'[INFO]: Removing existing deployed files.')
    shutil.rmtree(deploy_path)

    print(f'[INFO]: Copying dist files to deployment path')
    shutil.copytree(dist_path, deploy_path)

    print('[SUCCESS]: Deployment operation complete.')


if __name__ == '__main__':
    main()