<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->

![[Python][Python-url]][python-shield]
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License: MPL 2.0][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
<h3 align="center">HGT_Tool</h3>

  <p align="center">
    project_description
    <br />
    <a href="https://github.com/aasaporito/HGT/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/aasaporito/HGT/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
      <ul>
         <li><a href="#frag_ex">Fragmenting Mode Example</a></li></li>
         <li><a href="#roll_ex">Rolling Window Mode Example </a></li>
</ul>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

`project_description`

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* <a href="https://www.python.org/downloads/"> Python >= 3.7 </a>
* pip (This project can also be installed via <a href="https://python-poetry.org/"> Poetry</a>)


### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/aasaporito/HGT.git
   ```
2. Install pip packages 
   ```sh
   pip3 install tqdm
   ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
<a id="frag_ex"></a>
### Fragmenting Mode Example:
1. From the HGT directory, generate sequences at a rate of 10 per sequence:
      ```sh
    ./run.sh --frag --size 10 --min-frags 10 --input <input_file.sam>
      ```
2. Fragmented output for realignment can be found at HGT/tmp/fragments.fasta
3. Run aligner of choice on fragments.fasta.
4. Call output processor on the re-aligned sequences.
    ```sh
   ./run.sh --frag --size 10 --min-frags 10 --input <re-aligned.sam> --results
   ```
5. Results will be generated at HGT/Output/Fragment_Results_id.txt
<p align="right">(<a href="#readme-top">back to top</a>)</p>




<a id="roll_ex"></a>
### Rolling Window Mode Example:
1. From the HGT directory, generate rolling splits in increments of 10%.
      ```sh
    ./run.sh --rolling --window 10 --input <input_file.sam>
      ```
2. Sliced output for realignment can be found at HGT/tmp/rolling_window.fasta
3. Run aligner of choice on rolling_window.fasta. (It is recommended to run with no secondary matches and saving successful aligns only)
4. Call output processor on the re-aligned sequences.
    ```sh
   ./run.sh --rolling --window 10 --input <re-aligned.sam> --results
   ```
5. Results will be generated at HGT/Output/Rolling_Window_Results_id.txt

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- Parameters -->
### Parameters
| Argument       | Function                                                                                                                                                           | Default                     | Requirements                      |
|----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------|-----------------------------------|
| `-h, --help`   | Displays arguments and usage                                                                                                                                       | <center>--</center>         | <center>--</center>               |
| `-f, --frag`   | Indicates that you want to run the program in fragmenting mode.  Default: off.                                                                                     | <center>--</center>         | Must be specified or -r/--rolling |
| `-r, --rolling` | Indicates that you want to run the program in rolling window mode.  Default: off.                                                                                  | <center>--</center>         | Must be specified or -f/--frag    |
| `-i, --input`  | Your input aligned .sam file with path. Applies to both initial runs and result processing mode.                                                                   | <center>--</center>         | Mandatory                         |
| `--results`    | Indicates to run the result processor for the specified .sam file and parameters. Generally should be called in addition to all original arguements during step 1. | <center>---</center>        | <center>---</center>              |
| `-s, --size`   | Specifies the amount of fragments to create per sequence.                                                                                                          | <center> 10 fragments       | <center>-f/--frag                 |
| `-m, --min-frags` | Specifies the amount of fragments that must be aligned to qualify for horizontal gene transfer candidacy. Must be <= -s/--size. <br/> *In fragmenting mode --min-frags can be changed at result processing time.                                   | <center> Equal to -s/--size | <center> -f/--frag                |
| `-w, --window` | Specifies the window step size for rolling mode.                                                                                                                   | <center> 10%                | <center> -r/--rolling             |


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the Mozilla Public License Version 2.0 License. See `LICENSE.txt` for more information.
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact
##### Author: 
Aaron Saporito - [LinkedIn](https://www.linkedin.com/in/aaron-saporito) - [GitHub](https://github.com/aasaporito)

Project Link: [https://github.com/aasaporito/HGT](https://github.com/aasaporito/HGT)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
* <a href="https://www.conncoll.edu/directories/faculty-profiles/stephen-douglass/"> Dr. Stephen Douglass </a>
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/aasaporito/HGT.svg?style=for-the-badge
[contributors-url]: https://github.com/aasaporito/HGT/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/aasaporito/HGT.svg?style=for-the-badge
[forks-url]: https://github.com/aasaporito/HGT/network/members
[stars-shield]: https://img.shields.io/github/stars/aasaporito/HGT.svg?style=for-the-badge
[stars-url]: https://github.com/aasaporito/HGT/stargazers
[issues-shield]: https://img.shields.io/github/issues/aasaporito/HGT.svg?style=for-the-badge
[issues-url]: https://github.com/aasaporito/HGT/issues
[license-shield]: https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg?style=for-the-badge
[license-url]: https://github.com/aasaporito/HGT/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/aaron-saporito

[JQuery-url]: https://jquery.com
[Python-url]: https://python.org
[Python-shield]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white